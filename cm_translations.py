# Copyright 2017 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy

translations = {
    'es': {
        # Toolbars
        ("Operator", "Start Simulation"): "Empezar Simulación",
        ("Operator", "Stop Simulation"): "Detener Simulación",
        ("*", "Simulation Start Frame"): "Empezar Simulación por Frame",
        ("*", "Simulation End Frame"): "Fin de Simulación por Frame",
        ("*", "Utilities"): "Utilitarios",
        ("Operator", "Place Deferred Geometry"): "Lugar sin Geometría",
        ("Operator", "Switch Dupli Groups"): "Cambiar Grupos Duplicados",
        ("*", "Dupli Group Suffix"): "Duplicar Grupos Por Sufijo",
        ("*", "Dupli Group Target"): "Duplicar Grupos Por objetivo",
        ("*", "Agents"): "Agentes",
        ("*", "Group Name"): "Nombre del Grupo",
        ("*", "Number | Origin"): "Número | Origen",
        ("*", "View Group Details"): "Ver Detalles del Grupo",
        ("*", "No group selected"): "Grupo No Seleccionado",
        ("*", "Manual Agents"): "Agentes Manuales",
        ("*", "Brain Type"): "Tipo de Lógica",
        ("Operator", "Create Manual Agents"): "Operador, Crear Agentes Manuales",
        ("*", "Armature Action"): "Acción de Armadura",
        ("*", "Motion Action"): "Acción de Movimiento",
        ("*", "Action pairings:"): "Acción de emparejamiento",
        ("*", "Events"): "Eventos",
        ("*", "Time+Volume"): "Tiempo y Volumen",
        ("*", "Road"): "Camino",
        ("*", "Bidirectional"): "Bidireccional",
        ("Operator", "Breadth First Search To Direct Edges"): "Primera búsqueda de aplitud para Direccionar Bordes",
        ("Operator", "Depth First Search To Direct Edges"): "Primera búsqueda de profundidad para direccionar Bordes",
        ("Operator", "Switch The Direction Of The Connected Edges"): "Cambio de dirección de los bordes conectados",
        ("Operator", "Switch The Direction Of The Selected Edges"): "Cambio de dirección de los bordes seleccionados",
        ("*", "Lane Separation"): "Separación de carriles",
        ("Operator", "Draw Directions"): "Dibujar direcciones",
        # User Prefs
        ("*", "General Settings"): "Congiguración General",
        ("*", "Addon Update Settings"): "Configuarción de actualización del Addon",
        ("*", "Debug Options"): "Opciones de Debug",
        ("*", "Use Custom Icons"): "Usar iconos personalizados",
        ("*", "Start Animation Automatically"): "Empezar animación automáticamente",
        ("*", "Ask To Save"): "Preguntar al momento de Guardar",
        ("*", "Use Node Color"): "Usar color de Nodos",
        ("*", "Show Debug Options"): "Mostrar opciones de Debug",
        ("Operator", "Our Website"): "Nuestro Sitio Web",
        ("Operator", "Email Us"): "Nuestro Correo Electrónico",
        ("Operator", "Save Settings"): "Guardar Configuraciones",
        ("*", "Updater Settings"): "Actualizar Configuraciones",
        ("*", "Auto-check for Update"): "Comprobar Automáticamente la Actualización",
        ("*", "Interval between checks"): "Intervalo de tiempo entre comprobaciones",
        ("*", "Months"): "Meses",
        ("*", "Days"): "Días",
        ("*", "Hours"): "Horas",
        ("*", "Minutes"): "Minutos",
        ("Operator", "Check now for crowdmaster update"): "Comprobar para Actualizar CrowdMaster",
        ("Operator", "Install latest develop / old version"): "Instalar versión de desarrollo / Versión anterior",
        ("Operator", "Restore addon backup (none found)"): "Restaurar Resguardo del Addon (No encontrado)",
        ("Operator", "Run Short Tests"): "Ejecutar Tests Cortos",
        ("Operator", "Run Long Tests"): "Ejecutar Tests Largos",
        ("*", "Show Debug Timings"): "Ejecutar Debug por Horarios",
        ("*", "Enable Show Debug Options to access these settings (only for developers)."): "Activar: Mostrar opciones de Debug para acceder a estas Configuraciones (Sólo para Desarrolladores)",
        # Node names
        # generation
        ("*", "Constrain Bone"): "Coacción del Hueso",
        ("*", "Link Armature"): "Conectar Armadura",
        ("*", "Modify Bone"): "Modificar el Hueso",
        ("*", "Add To Group"): "Agregar al Grupo",
        ("*", "Combine"): "Combinar",
        ("*", "Point Towards"): "Hacia el punto",
        ("*", "Random Material"): "Material Aleatorio",
        ("*", "Set Tag"): "Configurar Tag",
        ("*", "Positioning"): "Posicionamiento",
        ("*", "Formation"): "Formación",
        ("*", "Ground"): "Terreno",
        # simulation
        ("*", "Print"): "Impresión",
        ("*", "Graph"): "Gráfico",
        ("*", "Map"): "Mapeado",
        ("*", "Logic"): "Lógica",
        ("*", "Strong"): "Fuerte",
        ("*", "Weak"): "Débil",
        # Node props
        # simulation
        ("*", "Agent Info"): "Información del Agente",
        ("*", "Agent Info Options"): "Opciones de Información del Agente",
        ("*", "Get Tag Name"): "Obtener Nombre de etiqueta",
        ("*", "Get Tag"): "Obtener Etiqueta",
        ("*", "Heading rx"): "Encabezado rx",
        ("*", "Heading rz"): "Encabezado rz",
        ("*", "Flocking Input"): "Entrada de Bandada",
        ("*", "Translation Axis"): "Ejes de Transalción",
        ("*", "Cohere"): "Adherirse",
        ("*", "Formation Group"): "Grupo de Formación",
        ("*", "Ground Group"): "Grupo de Terreno",
        ("*", "Ground Options"): "Opciones de Grupo",
        ("*", "ahead rx"): "rx Delante",
        ("*", "ahead rz"): "rz Delante",
        ("*", "Noise Options"): "Opciones de Ruido",
        ("*", "Agent Random"): "Agentes de manera Aleatoria",
        ("*", "Path Name"): "Nombre de Ruta",
        ("*", "Prediction"): "Predicción",
        ("*", "Minus Radius"): "Radio Menor",
        ("*", "State Options"): "Opciones de Estado",
        ("*", "Query tag"): "Etiqueta de Consulta",
        ("*", "World Options"): "Opciones Generales",
        ("*", "Event"): "Evento",
        ("*", "Time Multiplier"): "Multiplicador de tiempo",
        ("*", "Sound Options"): "Opciones de sonido",
        ("*", "Position X"): "Posición en X",
        ("*", "Position Y"): "Posición en Y",
        ("*", "Position Z"): "Posición en Z",
        ("*", "Shape Key Name"): "Forma nombre de clave",
        ("*", "Multi Input Type"): "Tipo de Entrada Múltiple",
        ("*", "Save To File"): "Guardar en Archivo",
        ("*", "Output Filepath"): "Salida de Ruta de Archivo",
        ("*", "Lower Input"): "Entrada mas Baja",
        ("*", "Upper Input"): "Entrada mas Alta",
        ("*", "Lower Output"): "Salda mas Baja",
        ("*", "Upper Output"): "Salida mas Alta",
        ("*", "Single Output"): "Salida Simple",
        ("*", "Include All"): "Incluir Todo",
        ("*", "State Length"): "Tamaño de Estado",
        ("*", "Cycle State"): "EStado del Ciclo",
        ("*", "Action Name"): "Nombre de la Acción",
        ("*", "Interupt State"): "Estado de Interrupción",
        ("*", "Sync State"): "Estado Síncrono",
        ("*", "Random wait time:"): "Espera de Tiempo Aleatorio",
        ("*", "Not equal"): "No es Igual",
        ("*", "Less than"): "Menos que",
        ("*", "Greater than"): "Mas grande que",
        ("*", "Least only"): "Sólo menos",
        ("*", "Most only"): "Sólo la Mayoría",
        ("*", "Set To"): "Configurado a",
        ("*", "Tag Name"): "Nombre de Etiqueta",
        ("*", "Use Threshold"): "Usar Límite",
        ("*", "Note Text"): "Texto de nota",
        ("Operator", "Grab Text From Clipboard"): "Agarrar Texto de ClipBoard",
        ("*", "Rotation Axis"): "Eje de Rotación",
        ("*", "Formation Options"): "Opciones de Formación",
        ("*", "Ground Ahead Offset"): "Encabezado de Desplazamiento",
        ("*", "Path Options"): "Opciones de Ruta",
        ("*", "In lane"): "En el Carril",
        ("*", "Search Distance"): "Buscar Distancia",
        ("*", "close"): "Cerca",
        ("*", "over"): "Encima",
        ("*", "Global Vel X"): "Velocidad Global en X",
        ("*", "Global Vel Y"): "Velocidad Global en Y",
        ("*", "Global Vel Z"): "Velocidad Global en Z",
        ("*", "Target Options"): "Opciones del Objetivo",
        ("*", "Arrived"): "Lllegada",
        ("*", "Event Name"): "Nombre de Evento",
        ("*", "Size Average"): "Tamaño Promedio",
        ("*", "Sum"): "Suma",
        ("*", "Lower Zero"): "Cero Bajo",
        ("*", "Lower One"): "único Bajo",
        ("*", "Upper One"): "Único Superior",
        ("*", "Upper Zero"): "Único Bajo",
        # generation
        ("*", "Parent Group"): "Emparentar Grupo",
        ("*", "Group File"): "Grupo de Archivo",
        ("*", "Duplicates Directory"): "Duplicar Archivo",
        ("*", "Rig Object"): "Objet Rig",
        ("*", "Additional Groups"): "Grupos Adicionales",
        ("*", "Parent To (Bone)"): "Emparentar a (Hueso)",
        ("*", "Geo Switch"): "Cambiar Geo",
        ("*", "Defer Geometry"): "Aplazar Geometría",
        ("*", "Group name:"): "Nombre de Grupo",
        ("*", "Point to Object"): "Apuntar al Objeto",
        ("*", "Point Type"): "Tipo de Apunte",
        ("*", "Min Rand Rotation"): "Mínima Rotación Aleatoria",
        ("*", "Max Rand Rotation"): "Máxima Rotación Aleatoria",
        ("*", "Min Rand Scale"): "Mínima Escala Aleatoria",
        ("*", "Max Rand Scale"): "Máxima Escala Aleatoria",
        ("*", "Target Material"): "Material Seleccionado",
        ("*", "Template Switch"): "Cambiado de Plantilla",
        ("*", "Formation Positioning"): "Posicionamiento de Formacion",
        ("*", "Number of Agents"): "Número de Agentes",
        ("*", "Rows"): "Filas",
        ("*", "Row Margin"): "Margen de Filas",
        ("*", "Column Margin"): "Margen de Columna",
        ("*", "Guide Mesh"): "Guia de Malla",
        ("*", "Overwrite position"): "Sobre Escribir Posición",
        ("*", "Relax Iterations"): "Suavizar Iteracciones",
        ("*", "Relax Radius"): "Suavizar Radio",
        ("*", "Obstacles"): "Obstaculos",
        ("*", "Location Object"): "Ubicacion de Objeto",
        ("*", "Location Offset"): "Compensar Locación",
        ("*", "Rotation Offset"): "Compensar Rotación",
        ("*", "Group By Mesh Islands"): "Agrupar por Mallas Aisladas",
        ("*", "Sector"): "Sector",
        ("*", "Target Type"): "Tipo de Objetivo",
        ("*", "Target Positioning"): "Tipo de Posicionamiento",
        ("*", "Place"): "Lugar",
        ("*", "Guide Mesh"): "Guía de Malla",
        ("Operator", "Generate Agents"): "Generar Agentes",
        ("*", "Random Positioning"): "Posición Aleatoria",
        ("*", "Location Type"): "Tipo de Locación",
    }
}


def register():
    # Register translations
    bpy.app.translations.register(__name__, translations)


def unregister():
    # Unregister translations
    bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
    register()
