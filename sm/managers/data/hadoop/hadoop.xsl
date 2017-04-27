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


   <xsl:param name="vcpunumber" select="/discocomponent/dependencies/dependency[@name='parameters']/variable[@name='vcpunumber']/text()"/>
   <xsl:param name="memorysize" select="/discocomponent/dependencies/dependency[@name='parameters']/variable[@name='memorysize']/text()"/>

    <xsl:variable name="rampercontainer" select="hadoop:rampercontainer($memorysize,$vcpunumber)" />
    <xsl:variable name="containercount" select="hadoop:containercount($memorysize,$vcpunumber)" />

    <!--the following configuration values have been taken from-->
    <!--https://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.3.4/bk_installing_manually_book/content/determine-hdp-memory-config.html-->

    <!--Configuration File		Configuration Setting					Value Calculation-->
    <!--yarn-site.xml			yarn.nodemanager.resource.memory-mb		= containers * RAM-per-container-->
    <!--yarn-site.xml			yarn.scheduler.minimum-allocation-mb	= RAM-per-container-->
    <!--yarn-site.xml			yarn.scheduler.maximum-allocation-mb	= containers * RAM-per-container-->
    <!--mapred-site.xml			mapreduce.map.memory.mb					= RAM-per-container-->
    <!--mapred-site.xml			mapreduce.reduce.memory.mb				= 2 * RAM-per-container-->
    <!--mapred-site.xml			mapreduce.map.java.opts					= 0.8 * RAM-per-container-->
    <!--mapred-site.xml			mapreduce.reduce.java.opts				= 0.8 * 2 * RAM-per-container-->
    <!--mapred-site.xml			yarn.app.mapreduce.am.resource.mb		= 2 * RAM-per-container-->
    <!--mapred-site.xml			yarn.app.mapreduce.am.command-opts		= 0.8 * 2 * RAM-per-container-->

    <xsl:variable name="memorymb" select="$rampercontainer*$containercount"/>
    <xsl:variable name="minallocationmb" select="$rampercontainer"/>
    <xsl:variable name="maxallocationmb" select="$rampercontainer*$containercount"/>
    <xsl:variable name="mapmemorymb" select="$rampercontainer"/>
    <xsl:variable name="reducememorymb" select="2*$rampercontainer"/>
    <xsl:variable name="mapjavaopts" select="floor(0.8*$rampercontainer)"/>
    <xsl:variable name="reducejavaopts" select="floor(1.6*$rampercontainer)"/>
    <xsl:variable name="resourcemb" select="2*$rampercontainer"/>
    <xsl:variable name="commandopts" select="floor(0.8*$rampercontainer)"/>



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
            <parameter string="$memorymb$" replace="{$memorymb}" />
            <parameter string="$minallocationmb$" replace="{$minallocationmb}" />
            <parameter string="$maxallocationmb$" replace="{$maxallocationmb}" />
            <parameter string="$mapmemorymb$" replace="{$mapmemorymb}" />
            <parameter string="$reducememorymb$" replace="{$reducememorymb}" />
            <parameter string="$mapjavaopts$" replace="{$mapjavaopts}" />
            <parameter string="$reducejavaopts$" replace="{$reducejavaopts}" />
            <parameter string="$resourcemb$" replace="{$resourcemb}" />
            <parameter string="$commandopts$" replace="{$commandopts}" />
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
