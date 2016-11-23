<%inherit file="base.mako"/>
<%block name="content">
<div class="container">
  <div class="row">
    <div class="col-md-8">
      <div id="leaflet"></div>
    </div>
    <div class="col-md-4">
      <h3><center>${_('Projects Overview')}</center></h3>

    </div>
  </div>
</div>
<script>
<%
from geojson import dumps
%>
var project_areas = ${dumps(project_areas)|n};
</script>
<script src="${request.static_url('osmtm:static/js/lib/leaflet.js')}"></script>
<script type="text/javascript" src="${request.static_url('osmtm:static/js/overview.js')}"></script>
</%block>
