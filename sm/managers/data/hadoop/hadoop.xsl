<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:heat="heat.xsl"
    xmlns:hadoop="hadoop.xsl">
<!--
Copyright (c) 2017. Zuercher Hochschule fuer Angewandte Wissenschaften
All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Author: Balazs Meszaros
-->

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>



<!--not used-->

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



    <xsl:variable name="parameterreplace">
            <parameter string="$replicationfactor$" replace="3" />
        </xsl:variable>




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
            <xsl:value-of select="heat:replace(/discocomponent/globaloutput/text(),$parameterreplace)" />
            <xsl:value-of select="heat:replace(/discocomponent/hadoopstart/text(),$parameterreplace)" />
            <xsl:call-template name="slavesfile" />
            <xsl:value-of select="heat:replace(/discocomponent/hadoopend/text(),$parameterreplace)" />
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
