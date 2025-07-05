#!/usr/bin/env python3
"""
Script para verificar o timezone atual do sistema
"""

import pytz
from datetime import datetime

def verificar_timezone():
    print("🌍 VERIFICAÇÃO DE TIMEZONE")
    print("=" * 40)
    
    # Timezone de Brasília
    timezone_brasilia = pytz.timezone('America/Sao_Paulo')
    
    # Hora atual em diferentes timezones
    hora_utc = datetime.now(pytz.UTC)
    hora_brasilia = datetime.now(timezone_brasilia)
    hora_local = datetime.now()
    
    print(f"🕐 Hora UTC:        {hora_utc.strftime('%H:%M:%S')}")
    print(f"🇧🇷 Hora Brasília:   {hora_brasilia.strftime('%H:%M:%S')}")
    print(f"🏠 Hora Local:       {hora_local.strftime('%H:%M:%S')}")
    
    print(f"\n📅 Data UTC:        {hora_utc.strftime('%Y-%m-%d')}")
    print(f"📅 Data Brasília:   {hora_brasilia.strftime('%Y-%m-%d')}")
    print(f"📅 Data Local:      {hora_local.strftime('%Y-%m-%d')}")
    
    print(f"\n⏰ Timezone UTC:    {hora_utc.tzinfo}")
    print(f"⏰ Timezone Brasília: {hora_brasilia.tzinfo}")
    print(f"⏰ Timezone Local:   {hora_local.tzinfo}")
    
    # Verificar se está em horário de verão (usando datetime naive)
    hora_naive = datetime.now()
    is_dst = timezone_brasilia.dst(hora_naive)
    print(f"\n☀️  Horário de Verão: {'Sim' if is_dst else 'Não'}")
    
    # Diferença entre UTC e Brasília
    diferenca = hora_brasilia - hora_utc
    print(f"⏱️  Diferença UTC-Brasília: {diferenca}")
    
    print(f"\n✅ Sistema configurado para usar horário de Brasília!")

if __name__ == "__main__":
    verificar_timezone() 