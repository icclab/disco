<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:heat="heat.xsl"
    xmlns:shell="shell.xsl">

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- here start the function templates for composition -->
             <xsl:template name="createslaves">
           <xsl:param name="var" select="/discocomponent/properties/property[@name='slavecount']/@value"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <xsl:call-template name="createslaves">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>

				<xsl:call-template name="replace-string">
				  <xsl:with-param name="text" select="/discocomponent/slavetemplate/text()"/>
				  <xsl:with-param name="replace" select="'$slavenumber$'" />
				  <xsl:with-param name="with" select="$var"/>
				</xsl:call-template>

             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>

         <xsl:template name="slavestring">
           <xsl:param name="var" select="/discocomponent/properties/property[@name='slavecount']/@value"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <xsl:call-template name="slavestring">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>
<xsl:text>            $slave</xsl:text><xsl:value-of select="$var" /><xsl:text>address$: { get_attr: [disco_slave_</xsl:text><xsl:value-of select="$var" /><xsl:text>, first_address] }
</xsl:text>
             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>

         <xsl:template name="hostsfile">
           <xsl:param name="var" select="/discocomponent/properties/property[@name='slavecount']/@value"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <xsl:call-template name="hostsfile">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>

				<xsl:text>$slave</xsl:text><xsl:value-of select="$var" /><xsl:text>address$   </xsl:text><xsl:value-of select="/discocomponent/properties/property[@name='slavename']/@value" /><xsl:text>-</xsl:text><xsl:value-of select="$var" /><xsl:text>
</xsl:text>
             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>


		<xsl:template name="replace-string">
		    <xsl:param name="text"/>
		    <xsl:param name="replace"/>
		    <xsl:param name="with"/>
		    <xsl:choose>
		      <xsl:when test="contains($text,$replace)">
		        <xsl:value-of select="substring-before($text,$replace)"/>
		        <xsl:value-of select="$with"/>
        		<xsl:call-template name="replace-string">
		          <xsl:with-param name="text" select="substring-after($text,$replace)"/>
		          <xsl:with-param name="replace" select="$replace"/>
		          <xsl:with-param name="with" select="$with"/>
		        </xsl:call-template>
		        </xsl:when>
		      <xsl:otherwise>
		        <xsl:value-of select="$text"/>
		      </xsl:otherwise>
		    </xsl:choose>
		  </xsl:template>

    <!-- these were the function templates -->

    <xsl:variable name="parameterreplace">
            <parameter string="$masterimage$" replace="{/discocomponent/properties/property[@name='masterimage']/@value}" />
            <parameter string="$slaveimage$" replace="{/discocomponent/properties/property[@name='slaveimage']/@value}" />
            <parameter string="$masterflavor$" replace="{/discocomponent/properties/property[@name='masterflavor']/@value}" />
            <parameter string="$slaveflavor$" replace="{/discocomponent/properties/property[@name='slaveflavor']/@value}" />
            <parameter string="$mastername$" replace="{/discocomponent/properties/property[@name='mastername']/@value}" />
            <parameter string="$slavename$" replace="{/discocomponent/properties/property[@name='slavename']/@value}" />
            <parameter string="$externalnetworkname$" replace="{/discocomponent/properties/property[@name='externalnetworkname']/@value}" />
            <parameter string="$networkname$" replace="{/discocomponent/properties/property[@name='networkname']/@value}" />
        </xsl:variable>

    <xsl:template match="/discocomponent/output">
        <xsl:if test="/discocomponent/properties/property[@name='state'][@value='end']">
            <xsl:variable name="globaloutput" select="heat:replace(/discocomponent/globaloutput/text(),$parameterreplace)" />
            <xsl:copy>
                <xsl:value-of select="shell:indentshell($globaloutput)" />
                <!-- insert slaves and Heat parameters for replacing here at this point -->
                <xsl:text>          params:
</xsl:text><xsl:call-template name="slavestring" />
<xsl:text>
            $sshprivatekey$: { get_attr: [sshkey, private_key] }
            $sshpublickey$: { get_attr: [sshkey, public_key] }
</xsl:text>
			<xsl:call-template name="createslaves" />
                <xsl:value-of select="heat:replace(/discocomponent/outputtemplate/text(),$parameterreplace)" />
            </xsl:copy>
        </xsl:if>


        <xsl:if test="/discocomponent/properties/property[@name='state'][@value='start']">
            <xsl:copy>
                <xsl:value-of select="heat:replace(/discocomponent/parameterssection/text(),$parameterreplace)" />
                <xsl:value-of select="heat:replace(/discocomponent/resourcessection/text(),$parameterreplace)" />
            </xsl:copy>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
