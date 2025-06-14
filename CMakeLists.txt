set(Namespace_SRCS
        freecad/StructureTools2/init_gui.py
        freecad/StructureTools2/__init__.py
        freecad/StructureTools2/my_numpy_function.py
        freecad/StructureTools2/version.py
        freecad/StructureTools2/resources/cool.svg
        freecad/StructureTools2/resources/translations/StructureTools_es-ES.qm
        freecad/StructureTools2/resources/translations/StructureTools_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/StructureTools2" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
