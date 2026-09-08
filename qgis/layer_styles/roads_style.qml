<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" version="3.28.0" hasScaleBasedVisibilityFlag="0">
  <renderer-v2 type="categorizedSymbol" attr="category" symbollevels="1">
    <categories>
      <category value="National Highway / Expressway" symbol="0" label="National Highway / Expressway" render="true"/>
      <category value="Primary Arterial Road" symbol="1" label="Primary Arterial Road" render="true"/>
      <category value="Secondary / Connector Road" symbol="2" label="Secondary / Connector Road" render="true"/>
    </categories>
    <symbols>
      <symbol type="line" name="0" alpha="1" clip_to_extent="1">
        <layer pass="3" class="SimpleLine" locked="0">
          <prop k="line_color" v="217,119,6,255"/>
          <prop k="line_width" v="1.2"/>
          <prop k="line_style" v="solid"/>
          <prop k="joinstyle" v="round"/>
          <prop k="capstyle" v="round"/>
        </layer>
      </symbol>
      <symbol type="line" name="1" alpha="1" clip_to_extent="1">
        <layer pass="2" class="SimpleLine" locked="0">
          <prop k="line_color" v="37,99,235,255"/>
          <prop k="line_width" v="0.85"/>
          <prop k="line_style" v="solid"/>
          <prop k="joinstyle" v="round"/>
          <prop k="capstyle" v="round"/>
        </layer>
      </symbol>
      <symbol type="line" name="2" alpha="1" clip_to_extent="1">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="line_color" v="100,116,139,255"/>
          <prop k="line_width" v="0.5"/>
          <prop k="line_style" v="solid"/>
          <prop k="joinstyle" v="round"/>
          <prop k="capstyle" v="round"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
</qgis>
