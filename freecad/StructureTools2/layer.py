class Layer():
      def __init__(self, obj):
        obj.addExtension("App::GeoFeatureGroupExtensionPython")

class LayerViewProvider():
      def __init__(self, obj):
        self.obj = obj
        self.obj.ViewObject.addExtension("Gui::ViewProviderGeoFeatureGroupExtensionPython")
        self.obj.ViewObject.Proxy = self

      def getIcon(self):
        return self.obj.getIcon()
