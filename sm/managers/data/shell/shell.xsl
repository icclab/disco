<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:shell="shell.xsl">

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

     <xsl:template name="sshslaves">
           <xsl:param name="var" select="/discocomponent/dependencies/dependency[@name='heat'][@state='start']/variable[@name='slavecount']/text()"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <xsl:call-template name="sshslaves">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>
<xsl:text>$slave</xsl:text><xsl:value-of select="$var" /><xsl:text>address$
</xsl:text>
             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>


         <xsl:template name="hostsfile">
           <xsl:param name="var" select="/discocomponent/dependencies/dependency[@name='heat'][@state='start']/variable[@name='slavecount']/text()"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <xsl:call-template name="hostsfile">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>

				<xsl:text>$slave</xsl:text><xsl:value-of select="$var" /><xsl:text>address$   </xsl:text><xsl:value-of select="/discocomponent/dependencies/dependency[@name='heat'][@state='start']/variable[@name='slavename']/text()" /><xsl:text>-</xsl:text><xsl:value-of select="$var" /><xsl:text>
</xsl:text>
             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>

    <xsl:template match="/discocomponent/output">
        <xsl:copy>
            <xsl:if test="/discocomponent/properties/property[@name='state']/@value='start'">
                <xsl:value-of select="/discocomponent/outputfirst/text()" />
                <xsl:call-template name="hostsfile" />
                <xsl:value-of select="/discocomponent/outputsecond/text()" />
                <xsl:call-template name="sshslaves" />
                <xsl:value-of select="/discocomponent/outputthird/text()" />

                <!--<xsl:call-template name="slavesfile" />-->
                <!--<xsl:value-of select="/discocomponent/outputfourth/text()" />-->
                <!--<xsl:call-template name="slavesfile" />-->
                <!--<xsl:value-of select="/discocomponent/outputfifth/text()" />-->
            </xsl:if>
            <xsl:if test="/discocomponent/properties/property[@name='state']/@value='end'">
                <xsl:value-of select="/discocomponent/globaloutput/text()" />
                <xsl:value-of select="/discocomponent/outputend/text()" />
            </xsl:if>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/discocomponent/properties/property[@name='outputtype']/@value">
      <xsl:if test="/discocomponent/properties/property[@name='state']/@value='end'">
        <xsl:attribute name="value">replace</xsl:attribute>
      </xsl:if>
      <xsl:if test="/discocomponent/properties/property[@name='state']/@value!='end'">
        <xsl:attribute name="value">
          <xsl:value-of select="/discocomponent/properties/property[@name='outputtype']/@value" />
        </xsl:attribute>
      </xsl:if>
    </xsl:template>
</xsl:stylesheet>
