<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:spark="spark.xsl">


    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>


         <xsl:template name="slavesfile">
           <xsl:param name="var" select="/discocomponent/dependencies/dependency[@name='heat'][@state='start']/variable[@name='slavecount']/text()"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <xsl:call-template name="slavesfile">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>
<xsl:text>$slavename$-</xsl:text><xsl:value-of select="$var" /><xsl:text>
</xsl:text>
             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>

    <xsl:template match="/discocomponent/output">
        <xsl:copy>
            <xsl:value-of select="/discocomponent/sparkstart/text()" />
            <xsl:call-template name="slavesfile" />
            <xsl:value-of select="/discocomponent/sparkend/text()" />
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
