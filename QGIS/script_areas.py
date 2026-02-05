import geopandas as gpd
import matplotlib.pyplot as plt

# Adicionar caminhos
path_para = "/home/..."
path_prodes = "/home/..." 

target_crs = 5880  # SIRGAS 2000

try:
    print("1. Carregando e processando geometrias...")
    # Leitura do limite estadual
    gdf_para = gpd.read_file(path_para).to_crs(epsg=target_crs)
    
    # Filtro espacial (Bounding Box) para acelerar a leitura do PRODES
    bbox_para = tuple(gdf_para.to_crs(epsg=4674).total_bounds)
    gdf_prodes = gpd.read_file(path_prodes, bbox=bbox_para).to_crs(epsg=target_crs)

    # Correção de erros topológicos (buffer 0)
    gdf_para['geometry'] = gdf_para.geometry.buffer(0)
    gdf_prodes['geometry'] = gdf_prodes.geometry.buffer(0)

    # Recorte (Clip) do desmatamento para o molde do Pará
    print("2. Recortando dados para o Estado do Pará...")
    gdf_prodes_para = gpd.clip(gdf_prodes, gdf_para)

    # --- CÁLCULO DAS ÁREAS ---
    
    # A_total: Área Geográfica Total do Estado
    area_total_km2 = gdf_para.geometry.area.sum() / 10**6

    # A_desmatada: Soma de todos os polígonos de desmatamento histórico até 2024
    desmatamento_acumulado = gdf_prodes_para[gdf_prodes_para['year'] <= 2024]
    area_desmatada_km2 = desmatamento_acumulado.geometry.area.sum() / 10**6
    
    # A_preservada: O que resta de floresta
    area_preservada_km2 = area_total_km2 - area_desmatada_km2

    # Cálculo dos Percentuais
    pct_preservado = (area_preservada_km2 / area_total_km2)
    pct_desmatado = (area_desmatada_km2 / area_total_km2)

    print(f"\n=== RESULTADOS FINAIS 2024 ===")
    print(f"Área Total:       {area_total_km2:,.2f} km²")
    print(f"Área Desmatada:   {area_desmatada_km2:,.2f} km² ({pct_desmatado*100:.2f}%)")
    print(f"Área Preservada:  {area_preservada_km2:,.2f} km² ({pct_preservado*100:.2f}%)")

except Exception as e:
    print(f"Erro no processamento: {e}")