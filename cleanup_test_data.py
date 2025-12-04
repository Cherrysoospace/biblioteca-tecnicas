"""
Script de Limpieza de Datos de Prueba

Este script limpia usuarios de prueba que fueron creados durante la ejecución de tests
y asegura la integridad referencial de la base de datos.

Funcionalidades:
1. Identifica usuarios inválidos (no existentes en users.json)
2. Elimina préstamos con usuarios inválidos
3. Elimina reservas con usuarios inválidos
4. Reporta estadísticas de limpieza
"""

import json
import os
from datetime import datetime


def load_json_file(filepath):
    """Cargar archivo JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Archivo no encontrado: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"⚠️ Error al decodificar JSON: {filepath}")
        return []


def save_json_file(filepath, data):
    """Guardar archivo JSON."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error al guardar {filepath}: {e}")
        return False


def cleanup_test_data():
    """Limpiar datos de prueba de la base de datos."""
    
    print("\n" + "="*70)
    print("LIMPIEZA DE DATOS DE PRUEBA")
    print("="*70)
    
    # Rutas de archivos
    data_dir = "data"
    users_file = os.path.join(data_dir, "users.json")
    loans_file = os.path.join(data_dir, "loan.json")
    reservations_file = os.path.join(data_dir, "reservations.json")
    
    # Cargar datos
    print("\n📂 Cargando archivos...")
    users = load_json_file(users_file)
    loans = load_json_file(loans_file)
    reservations = load_json_file(reservations_file)
    
    if not users:
        print("❌ No se pudo cargar users.json - abortando limpieza")
        return False
    
    # Obtener IDs de usuarios válidos
    valid_user_ids = {user['id'] for user in users}
    print(f"   ✅ {len(valid_user_ids)} usuarios válidos encontrados")
    print(f"   📊 {len(loans)} préstamos totales")
    print(f"   📊 {len(reservations)} reservas totales")
    
    # Identificar préstamos inválidos
    print("\n🔍 Analizando préstamos...")
    invalid_loans = []
    valid_loans = []
    
    for loan in loans:
        user_id = loan.get('user_id')
        if user_id not in valid_user_ids:
            invalid_loans.append(loan)
            print(f"   ❌ Préstamo inválido: {loan['loan_id']} - Usuario: {user_id}")
        else:
            valid_loans.append(loan)
    
    # Identificar reservas inválidas
    print("\n🔍 Analizando reservas...")
    invalid_reservations = []
    valid_reservations = []
    
    for reservation in reservations:
        user_id = reservation.get('user_id')
        if user_id not in valid_user_ids:
            invalid_reservations.append(reservation)
            print(f"   ❌ Reserva inválida: {reservation['reservation_id']} - Usuario: {user_id}")
        else:
            valid_reservations.append(reservation)
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE LIMPIEZA")
    print("="*70)
    print(f"Préstamos inválidos encontrados: {len(invalid_loans)}")
    print(f"Reservas inválidas encontradas: {len(invalid_reservations)}")
    
    if not invalid_loans and not invalid_reservations:
        print("\n✅ BASE DE DATOS LIMPIA - No se requiere limpieza")
        return True
    
    # Confirmar limpieza
    print("\n" + "="*70)
    print("¿Desea proceder con la limpieza? (s/n): ", end="")
    response = input().strip().lower()
    
    if response != 's':
        print("❌ Limpieza cancelada por el usuario")
        return False
    
    # Guardar datos limpios
    print("\n💾 Guardando datos limpios...")
    
    if invalid_loans:
        if save_json_file(loans_file, valid_loans):
            print(f"   ✅ {len(invalid_loans)} préstamos eliminados")
        else:
            print(f"   ❌ Error al guardar préstamos")
            return False
    
    if invalid_reservations:
        if save_json_file(reservations_file, valid_reservations):
            print(f"   ✅ {len(invalid_reservations)} reservas eliminadas")
        else:
            print(f"   ❌ Error al guardar reservas")
            return False
    
    # Crear backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\n📦 Creando backup de datos eliminados...")
    
    if invalid_loans or invalid_reservations:
        backup_data = {
            "timestamp": timestamp,
            "invalid_loans": invalid_loans,
            "invalid_reservations": invalid_reservations
        }
        backup_file = os.path.join(data_dir, f"cleanup_backup_{timestamp}.json")
        if save_json_file(backup_file, backup_data):
            print(f"   ✅ Backup guardado: {backup_file}")
    
    print("\n" + "="*70)
    print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
    print("="*70)
    print(f"Préstamos válidos restantes: {len(valid_loans)}")
    print(f"Reservas válidas restantes: {len(valid_reservations)}")
    
    return True


def validate_data_integrity():
    """Validar integridad de datos sin realizar cambios."""
    
    print("\n" + "="*70)
    print("VALIDACIÓN DE INTEGRIDAD DE DATOS")
    print("="*70)
    
    # Rutas de archivos
    data_dir = "data"
    users_file = os.path.join(data_dir, "users.json")
    loans_file = os.path.join(data_dir, "loan.json")
    reservations_file = os.path.join(data_dir, "reservations.json")
    
    # Cargar datos
    users = load_json_file(users_file)
    loans = load_json_file(loans_file)
    reservations = load_json_file(reservations_file)
    
    if not users:
        print("❌ No se pudo cargar users.json")
        return False
    
    # Validar
    valid_user_ids = {user['id'] for user in users}
    
    invalid_loans = [l for l in loans if l.get('user_id') not in valid_user_ids]
    invalid_reservations = [r for r in reservations if r.get('user_id') not in valid_user_ids]
    
    # Reporte
    print(f"\n📊 Usuarios válidos: {len(valid_user_ids)}")
    print(f"📊 Total préstamos: {len(loans)}")
    print(f"📊 Total reservas: {len(reservations)}")
    
    print(f"\n🔍 Préstamos inválidos: {len(invalid_loans)}")
    if invalid_loans:
        for loan in invalid_loans:
            print(f"   ❌ {loan['loan_id']} - Usuario: {loan.get('user_id')}")
    
    print(f"\n🔍 Reservas inválidas: {len(invalid_reservations)}")
    if invalid_reservations:
        for res in invalid_reservations:
            print(f"   ❌ {res['reservation_id']} - Usuario: {res.get('user_id')}")
    
    if not invalid_loans and not invalid_reservations:
        print("\n✅ BASE DE DATOS ÍNTEGRA - Todos los usuarios son válidos")
        return True
    else:
        print("\n⚠️ SE ENCONTRARON PROBLEMAS DE INTEGRIDAD")
        print("\nEjecute cleanup_test_data() para limpiar los datos")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        # Solo validar, no limpiar
        validate_data_integrity()
    else:
        # Limpiar datos
        cleanup_test_data()
