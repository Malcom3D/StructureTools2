class Layer():
      def __init__(self, obj):
        obj.addExtension("App::GeoFeatureGroupExtensionPython")

class LayerViewProvider():
      def __init__(self, obj):
        obj.ViewObject.addExtension("Gui::ViewProviderGeoFeatureGroupExtensionPython")
        obj.ViewObject.Proxy = self

      def getIcon(self):
        return obj.getIcon()
