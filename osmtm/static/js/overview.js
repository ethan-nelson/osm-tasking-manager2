function createMap() {
  lmap = L.map('leaflet');
  var osmUrl='//tile-{s}.openstreetmap.fr/hot/{z}/{x}/{y}.png';
  var osmAttrib = 'OSM';
  var osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});
  lmap.addLayer(osm);

  if (project_areas && project_areas.features.length > 0) {
    var project = new L.geoJson(null, {
      style: {
        color: 'red',
        weight: 1
      }
    });
    project.addData(project_areas);
    project.eachLayer(function (layer) {
      layer.bindPopup(layer.feature.properties.popup);
    });
    lmap.addLayer(project);
    lmap.fitBounds(project.getBounds());
  }
}

createMap();
