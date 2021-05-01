layer  = iface.activeLayer()

new_feature = QgsFeature(layer.fields())
print(layer.fields())
geometry = QgsGeometry.fromWkt("POLYGON ((116.2460543030807969 39.8984874903392495, 116.2253731829767958 39.8845190740780282, 116.2337090654697818 39.8721772749945274, 116.2543901855737971 39.8861456912557486, 116.2460543030807969 39.8984874903392495))")
print(geometry)
new_feature.setGeometry(geometry)

layer.dataProvider().addFeatures([new_feature])

iface.mapCanvas().refresh()