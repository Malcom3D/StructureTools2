class Layer():
      def __init__(self, obj):
        obj.addExtension("App::GeoFeatureGroupExtensionPython")

class LayerViewProvider():
      def __init__(self, obj):
        obj.addExtension("Gui::ViewProviderGeoFeatureGroupExtensionPython")
        obj.setIcon(obj.getIcon)
        obj.Proxy = self
