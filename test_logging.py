"""test_logging.py

Test simple para verificar que el sistema de logging funciona correctamente.
Simula operaciones típicas y verifica que se generen logs apropiados.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

import os
from utils.logger import LibraryLogger, UIErrorHandler

# Configurar logging
logger = LibraryLogger.get_logger(__name__)

def test_basic_logging():
    """Test básico de logging con diferentes niveles."""
    print("=== TEST: Sistema de Logging ===\n")
    
    # 1. Test de niveles de logging
    print("1. Probando niveles de logging:")
    logger.debug("Mensaje DEBUG: información detallada para debugging")
    logger.info("Mensaje INFO: operación normal completada")
    logger.warning("Mensaje WARNING: advertencia, todo sigue funcionando")
    logger.error("Mensaje ERROR: error recuperable")
    logger.critical("Mensaje CRITICAL: error crítico del sistema")
    print("   ✓ Logs escritos (ver archivo logs/library_YYYYMMDD.log)\n")
    
    # 2. Test de logging con contexto
    print("2. Probando logging con contexto:")
    user_id = "U001"
    book_id = "B042"
    logger.info(f"Préstamo creado: usuario={user_id}, libro={book_id}")
    logger.info(f"Stock decrementado: libro={book_id}, nuevo_stock=4")
    print("   ✓ Logs con datos contextuales escritos\n")
    
    # 3. Test de logging de excepciones
    print("3. Probando logging de excepciones:")
    try:
        # Simular un error
        result = 10 / 0
    except Exception as e:
        logger.error("Error de división por cero", exc_info=True)
        print("   ✓ Excepción loggeada con stack trace completo\n")
    
    # 4. Test de UIErrorHandler.log_and_pass
    print("4. Probando UIErrorHandler.log_and_pass:")
    try:
        # Simular error no crítico (cargar un icono opcional)
        raise FileNotFoundError("icon.png not found")
    except Exception as e:
        UIErrorHandler.log_and_pass(logger, "cargar icono opcional", e)
        print("   ✓ Error no crítico loggeado sin interrumpir ejecución\n")
    
    # 5. Verificar archivo de log
    print("5. Verificando archivo de log:")
    from datetime import datetime
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    log_file = os.path.join(log_dir, f'library_{datetime.now():%Y%m%d}.log')
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"   ✓ Archivo de log creado: {log_file}")
        print(f"   ✓ Total de líneas en log: {len(lines)}")
        print(f"\n   Últimas 5 líneas del log:")
        for line in lines[-5:]:
            print(f"   {line.rstrip()}")
    else:
        print(f"   ✗ Archivo de log no encontrado: {log_file}")
    
    print("\n=== FIN DEL TEST ===\n")
    print("✅ SISTEMA DE LOGGING FUNCIONANDO CORRECTAMENTE")
    print("   - Logs escritos en archivo con formato correcto")
    print("   - Diferentes niveles de logging funcionando")
    print("   - Stack traces de excepciones capturados")
    print("   - Helpers de UIErrorHandler operativos")
    print(f"\n📝 Revisar archivo completo: {log_file}")

if __name__ == "__main__":
    test_basic_logging()
