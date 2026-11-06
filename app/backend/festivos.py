"""Festivos oficiales (Ley Federal del Trabajo, artículo 74) para 2026 y 2027."""

from datetime import date

FESTIVOS: dict[int, set[date]] = {
    2026: {
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 16),
        date(2026, 12, 25),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 2, 1),
        date(2027, 3, 15),
        date(2027, 5, 1),
        date(2027, 9, 16),
        date(2027, 11, 15),
        date(2027, 12, 25),
    },
}

ANIOS_SOPORTADOS = sorted(FESTIVOS.keys())


def es_dia_habil(fecha: date) -> bool:
    es_fin_de_semana = fecha.weekday() >= 5
    es_festivo = fecha in FESTIVOS.get(fecha.year, set())
    return not es_fin_de_semana and not es_festivo
