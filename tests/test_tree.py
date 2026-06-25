from markdown_parser import MarkdownTree


class TestInit:
    # Se ejecuta al crear un MarkdownTree()
    # Crea el nodo raíz con nivel 0 y título "ROOT"
    def test_crea_raiz_con_nivel_0_y_titulo_ROOT(self):
        tree = MarkdownTree()
        assert tree.root.level == 0
        assert tree.root.title == "ROOT"


class TestParse:
    # Texto sin encabezados: se guarda como contenido de la raíz
    def test_sin_encabezados_guarda_contenido_en_raiz(self):
        tree = MarkdownTree()
        tree.parse("Hola mundo\nEsto es texto plano")
        assert tree.root.content == ["Hola mundo\nEsto es texto plano"]

    # Un encabezado sin contenido extra
    def test_un_encabezado_sin_contenido(self):
        tree = MarkdownTree()
        tree.parse("# Titulo")
        assert len(tree.root.children) == 1
        assert tree.root.children[0].level == 1
        assert tree.root.children[0].title == "Titulo"
        assert tree.root.children[0].content == []

    # Un encabezado con contenido después
    def test_un_encabezado_con_contenido(self):
        tree = MarkdownTree()
        tree.parse("# Titulo\n\nEsto es contenido")
        assert tree.root.children[0].content == ["Esto es contenido"]

    # Varios encabezados del mismo nivel (while con 0 iteraciones)
    def test_varios_encabezados_mismo_nivel(self):
        tree = MarkdownTree()
        tree.parse("# A\n# B\n# C")
        assert len(tree.root.children) == 3

    # Encabezados de nivel descendente (while hace pop)
    def test_encabezados_distinto_nivel_con_pop(self):
        tree = MarkdownTree()
        tree.parse("## B\n# A")
        assert tree.root.children[0].title == "B"
        assert tree.root.children[0].level == 2
        assert tree.root.children[1].title == "A"
        assert tree.root.children[1].level == 1


class TestFindNodeByPath:
    # Ruta vacía: devuelve None
    def test_ruta_vacia_devuelve_None(self):
        tree = MarkdownTree()
        tree.parse("# A\n## B")
        assert tree.find_node_by_path("") is None

    # Ruta "ROOT": no hay hijo con ese título, devuelve None
    def test_ruta_ROOT_devuelve_None(self):
        tree = MarkdownTree()
        assert tree.find_node_by_path("ROOT") is None

    # Ruta de un nivel que existe
    def test_ruta_un_nivel_existente(self):
        tree = MarkdownTree()
        tree.parse("# Hola")
        node = tree.find_node_by_path("Hola")
        assert node is not None
        assert node.title == "Hola"

    # Ruta de un nivel que no existe
    def test_ruta_un_nivel_inexistente(self):
        tree = MarkdownTree()
        tree.parse("# A")
        assert tree.find_node_by_path("X") is None

    # Ruta multi-nivel existente (navega por A.B.C)
    def test_ruta_multinivel_existente(self):
        tree = MarkdownTree()
        tree.parse("# A\n## B\n### C")
        node = tree.find_node_by_path("A.B.C")
        assert node is not None
        assert node.title == "C"
        assert node.level == 3

    # Ruta multi-nivel donde un nivel intermedio no existe
    def test_ruta_multinivel_intermedio_inexistente(self):
        tree = MarkdownTree()
        tree.parse("# A\n## B")
        assert tree.find_node_by_path("A.X.Y") is None


class TestRemoveSection:
    # Eliminar una sección que existe y tiene padre
    def test_eliminar_seccion_existente(self):
        tree = MarkdownTree()
        tree.parse("# A\n## B")
        assert tree.remove_section("A.B") is True
        assert tree.find_node_by_path("A.B") is None

    # Eliminar una sección que no existe
    def test_eliminar_seccion_inexistente(self):
        tree = MarkdownTree()
        tree.parse("# A")
        assert tree.remove_section("X") is False

    # Eliminar la raíz (no tiene padre, debe fallar)
    def test_eliminar_raiz_devuelve_False(self):
        tree = MarkdownTree()
        assert tree.remove_section("ROOT") is False


class TestAddSection:
    # Agregar sección a la raíz usando ruta vacía
    def test_agregar_a_raiz(self):
        tree = MarkdownTree()
        node = tree.add_section("", "Nuevo")
        assert node is not None
        assert node.title == "Nuevo"
        assert node.level == 1
        assert node in tree.root.children

    # Agregar sección a un padre que existe
    def test_agregar_a_padre_valido(self):
        tree = MarkdownTree()
        tree.parse("# A")
        node = tree.add_section("A", "B")
        assert node is not None
        assert node.title == "B"
        assert node.level == 2
        assert node in tree.find_node_by_path("A").children

    # Agregar sección a un padre que no existe
    def test_agregar_a_padre_invalido_devuelve_None(self):
        tree = MarkdownTree()
        assert tree.add_section("X", "Nuevo") is None

    # Agregar sección con contenido
    def test_agregar_con_contenido(self):
        tree = MarkdownTree()
        node = tree.add_section("", "A", content="Hola")
        assert node.content == ["Hola"]

    # Agregar sección sin contenido
    def test_agregar_sin_contenido(self):
        tree = MarkdownTree()
        node = tree.add_section("", "A")
        assert node.content == []


class TestDump:
    # Árbol vacío devuelve string vacío
    def test_arbol_vacio(self):
        tree = MarkdownTree()
        assert tree.dump() == ""

    # Árbol con nodos devuelve markdown
    def test_arbol_con_nodos(self):
        tree = MarkdownTree()
        tree.parse("# A\n## B")
        salida = tree.dump()
        assert "# A" in salida
        assert "## B" in salida


class TestVisualize:
    # Solo verifica que no lanza excepción y muestra algo
    def test_visualize_funciona(self, capsys):
        tree = MarkdownTree()
        tree.parse("# A")
        tree.visualize()
        captured = capsys.readouterr()
        assert "# A" in captured.out


class TestAttachSubtree:
    # Adjuntar todo el árbol fuente a la raíz del destino
    def test_adjuntar_subarbol_completo_a_raiz(self):
        dest = MarkdownTree()
        dest.parse("# A")
        source = MarkdownTree()
        source.parse("# X\n# Y")
        attached = dest.attach_subtree("A", source)
        assert len(attached) == 2
        assert dest.find_node_by_path("A.X") is not None
        assert dest.find_node_by_path("A.Y") is not None

    # Adjuntar solo un subárbol específico del fuente
    def test_adjuntar_subarbol_especifico(self):
        dest = MarkdownTree()
        dest.parse("# A")
        source = MarkdownTree()
        source.parse("# X\n## Y\n### Z")
        attached = dest.attach_subtree("A", source, source_path="X.Y")
        assert len(attached) == 1
        assert dest.find_node_by_path("A.Y") is not None

    # Destino inválido devuelve lista vacía
    def test_adjuntar_destino_invalido(self):
        dest = MarkdownTree()
        source = MarkdownTree()
        source.parse("# X")
        result = dest.attach_subtree("INEXISTENTE", source)
        assert result == []

    # Origen inválido (ruta no existe) devuelve lista vacía
    def test_adjuntar_origen_invalido(self):
        dest = MarkdownTree()
        dest.parse("# A")
        source = MarkdownTree()
        source.parse("# X")
        result = dest.attach_subtree("A", source, source_path="INEXISTENTE")
        assert result == []

    # Origen es la raíz del fuente (source_path="ROOT")
    def test_adjuntar_origen_raiz(self):
        dest = MarkdownTree()
        dest.parse("# A")
        source = MarkdownTree()
        source.parse("# X\n## Y")
        attached = dest.attach_subtree("A", source, source_path="ROOT")
        assert len(attached) == 1
        assert dest.find_node_by_path("A.X") is not None
        assert dest.find_node_by_path("A.X.Y") is not None
