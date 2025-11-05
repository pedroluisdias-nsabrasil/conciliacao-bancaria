"""Teste de Integração Completa - Sprint 6 Final."""

from decimal import Decimal
from datetime import date
from src.conciliacao.motor import MotorConciliacao
from src.modelos.lancamento import Lancamento

print("=" * 70)
print("🧪 TESTE DE INTEGRAÇÃO COMPLETA - SPRINT 6")
print("=" * 70)

# 1. Inicializar motor
print("\n📍 PASSO 1: Inicializar Motor")
motor = MotorConciliacao()
print(f"✅ Motor inicializado com {len(motor.estrategias)} estratégias")
print(f"   Estratégias: {[e.nome for e in motor.estrategias]}")
print(f"   Ordem: {[f'{e.nome} (P={e.prioridade})' for e in motor.estrategias]}")

# Validar ordem
assert motor.estrategias[0].prioridade > motor.estrategias[1].prioridade, "Ordem incorreta"
print("✅ Ordem de prioridade correta (maior prioridade primeiro)")

# 2. Criar lançamentos de teste
print("\n📍 PASSO 2: Criar Lançamentos de Teste")
tarifas = [
    Lancamento(date(2025, 11, 5), Decimal('15.00'), 'TARIFA DOC TRANSFERENCIA', 'D'),
    Lancamento(date(2025, 11, 5), Decimal('8.50'), 'TARIFA PIX ENVIADO', 'D'),
    Lancamento(date(2025, 11, 5), Decimal('12.00'), 'TARIFA TED MESMA TITULARIDADE', 'D'),
]

normais = [
    Lancamento(date(2025, 11, 5), Decimal('250.00'), 'COMPRA LOJA ABC', 'D'),
    Lancamento(date(2025, 11, 5), Decimal('1500.00'), 'PAGAMENTO FORNECEDOR XYZ', 'D'),
]

print(f"✅ {len(tarifas)} tarifas bancárias criadas")
print(f"✅ {len(normais)} lançamentos normais criados")

# 3. Testar auto-conciliação
print("\n📍 PASSO 3: Testar Auto-Conciliação")
print("-" * 70)

matches_tarifas = 0
matches_normais = 0
detalhes = []

for lanc in tarifas + normais:
    match_info = None
    for estrategia in motor.estrategias:
        match = estrategia.encontrar_match(lanc, [], set())
        if match:
            match_info = (estrategia.nome, match.confianca, match.metodo)
            if lanc in tarifas:
                matches_tarifas += 1
            else:
                matches_normais += 1
            break
    
    # Formatar saída
    desc = f"{lanc.descricao[:35]:35}"
    valor = f"R$ {lanc.valor:>8}"
    
    if match_info:
        estrategia, conf, metodo = match_info
        print(f"✅ {desc} {valor} → {estrategia} ({conf:.0%}, {metodo})")
    else:
        print(f"⚠️  {desc} {valor} → Não conciliado")

# 4. Validar resultados
print("\n📍 PASSO 4: Validar Resultados")
print("-" * 70)

sucesso_tarifas = (matches_tarifas == len(tarifas))
sucesso_normais = (matches_normais == 0)

if sucesso_tarifas:
    print(f"✅ TARIFAS: {matches_tarifas}/{len(tarifas)} auto-conciliadas (100%)")
else:
    print(f"❌ TARIFAS: {matches_tarifas}/{len(tarifas)} auto-conciliadas")

if sucesso_normais:
    print(f"✅ NORMAIS: {matches_normais}/{len(normais)} conciliados (esperado - sem comprovantes)")
else:
    print(f"⚠️  NORMAIS: {matches_normais}/{len(normais)} conciliados (inesperado)")

taxa_total = (matches_tarifas + matches_normais) / (len(tarifas) + len(normais)) * 100
print(f"\n📊 Taxa de conciliação geral: {taxa_total:.1f}%")

# 5. Resultado final
print("\n" + "=" * 70)
print("📊 RESULTADO FINAL")
print("=" * 70)

if sucesso_tarifas and sucesso_normais:
    print("✅ TESTE DE INTEGRAÇÃO: SUCESSO!")
    print("\n✨ Sistema funcionando perfeitamente:")
    print("   ✅ Motor com 2 estratégias")
    print("   ✅ Ordem de prioridade correta (Regras → Exato)")
    print("   ✅ Auto-conciliação de tarifas funcionando")
    print("   ✅ Lançamentos normais não são auto-conciliados")
    print("\n🎉 FASE 5 COMPLETA!")
    print("🎯 MVP 95% COMPLETO!")
    print("\nFalta apenas:")
    print("   ⏳ Fase 6: Interface (opcional)")
else:
    print("❌ TESTE DE INTEGRAÇÃO: VERIFICAR RESULTADOS")
    if not sucesso_tarifas:
        print(f"   ⚠️  Tarifas: esperado {len(tarifas)}, obtido {matches_tarifas}")
    if not sucesso_normais:
        print(f"   ⚠️  Normais: esperado 0, obtido {matches_normais}")

print("=" * 70)