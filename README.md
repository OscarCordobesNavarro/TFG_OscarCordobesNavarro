# Proyecto de Optimización Combinatoria - Análisis de Herramientas de Generación de Código

Este repositorio contiene el código y los resultados del análisis de OptiMUS.

## 🗂️ Estructura del Repositorio

### Problemas de Optimización Analizados

El repositorio está organizado por tipo de problema, cada uno con sus respectivos archivos de código y datos:

#### 📦 **BPP** - Bin Packing Problem (Problema de Empaquetado)
- `Code.py`: Código generado en la primera iteración
- `Data.json` - `Data5.json`: 5 instancias de datos de prueba
- ✅ **Estado**: Generación exitosa (5 instancias completas)

#### 🎒 **Knapsack** - Problema de la Mochila
- `Code.py`: Código generado en la primera iteración
- `Data.json` - `Data5.json`: 5 instancias de datos de prueba
- ✅ **Estado**: Generación exitosa (5 instancias completas)

#### 🏭 **CFLP** - Capacitated Facility Location Problem
- `Code.py`: Código generado en la primera iteración
- `CodeMod.py`: Código modificado con correcciones de errores
- `Data.json`: Instancia de datos original
- `DataMod.json`: Datos modificados
- ⚠️ **Estado**: Requirió correcciones (primera iteración fallida)

#### 📏 **CPP** - Cutting and Packing Problem
- `Code.py`: Código generado en la primera iteración
- `CodeMod.py`: Código modificado con correcciones de errores
- `Data.json`: Instancia de datos original
- `DataMod.json`: Datos modificados
- ⚠️ **Estado**: Requirió correcciones (primera iteración fallida)

#### 🗺️ **TSP** - Traveling Salesman Problem
- `Code.py`: Código generado en la primera iteración
- `CodeMod.py`: Código modificado con correcciones de errores
- `Data.json`: Instancia de datos original
- `DataMod.json`: Datos modificados
- ⚠️ **Estado**: Requirió correcciones (primera iteración fallida)

#### 🚚 **VRP** - Vehicle Routing Problem
- `Code.py`: Código generado en la primera iteración
- `CodeMod.py`: Código modificado con correcciones de errores
- `DataMod.json`: Datos modificados
- ⚠️ **Estado**: Requirió correcciones (primera iteración fallida)

### 📁 Carpetas Especiales

#### **FormulacionesHTML/**
Contiene una instantánea en formato HTML de:
- Extracción de parámetros de la herramienta
- Cláusulas generadas directamente por la herramienta
- **Subcarpeta**: `FormulacionesTrasAjuste/` - Formulaciones después de ajustes

Los tipos de las variables aparecen en la instantánea de forma incorrecta, aparecen todos como binarias. Esto es un problema de la herramienta que realiza la extracción HTML

#### **PostAjustePrompts/**
Segunda iteración para los problemas que fallaron en la primera iteración:

- **CFLP/**: `CFLP_P.py` + 5 instancias de datos (`Data.json` - `Data5.json`)
- **CPP/**: `CPP_P.py` + 5 instancias de datos (`Data.json` - `Data5.json`)
- **TSP/**: `TSP_P.py` + 5 instancias de datos (`Data.json` - `Data5.json`)
- **VRP/**: `VRP_P.py` + 5 instancias de datos (`Data.json` - `Data5.json`)


### Nomenclatura de Archivos
- `Code.py`: Código original generado por la herramienta
- `CodeMod.py`: Código modificado manualmente para corregir errores
- `[Problema]_P.py`: Código generado en la segunda iteración (post-ajustes)
- `Data.json`: Instancia de datos principal
- `DataMod.json`: Datos modificados para funcionamiento correcto
- `Data2.json` - `Data5.json`: Instancias adicionales de datos de prueba

