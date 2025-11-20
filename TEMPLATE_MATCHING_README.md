# Sistema de Mascaramento de Dados Sensíveis com Template Matching

## 📋 Visão Geral

Este sistema mascara dados sensíveis em comprovantes de pagamento usando **template matching** ao invés de LLM. Ele compara a estrutura visual de cada arquivo com templates pré-configurados e aplica as coordenadas de mascaramento correspondentes.

## 🏗️ Estrutura de Diretórios

```
src/config/coordinates/
├── nu/
│   ├── coordinates_output_a.json
│   ├── coordinates_output_a.png
│   ├── coordinates_output_b.json
│   └── coordinates_output_b.png
├── bradesco/
│   ├── coordinates_output_pix.json
│   └── coordinates_output_pix.png
└── [outros_bancos]/
    └── ...
```

### Estrutura dos Templates

Cada template consiste em:

-   **`.json`**: Coordenadas das áreas sensíveis
-   **`.png`**: Imagem de referência (mascarada)

## 🔧 Como Criar Templates

### 1. Usar o Coordinate Selector

```bash
python coordinates_config_setter.py -i caminho/para/comprovante.jpg
```

**Passos:**

1. Desenhe retângulos sobre os dados sensíveis
2. Pressione **'q'** para sair
3. Serão gerados:
    - `coordinates_output.json` - coordenadas
    - `coordinates_output.png` - imagem mascarada

### 2. Organizar os Templates

```bash
# Criar diretório do banco se não existir
mkdir -p src/config/coordinates/nu

# Mover e renomear os arquivos
mv coordinates_output.json src/config/coordinates/nu/coordinates_output_tipo1.json
mv coordinates_output.png src/config/coordinates/nu/coordinates_output_tipo1.png
```

## 🚀 Usar o Sistema de Mascaramento

```bash
python sensitive_data_masker.py -p ./test/ -o ./masked_output/
```

### Parâmetros

-   `-p, --path`: Diretório com os arquivos para mascarar
-   `-o, --output`: Diretório de saída (padrão: `classify_output`)

## ⚙️ Como Funciona

### 1. Carregamento de Templates

O sistema carrega automaticamente todos os templates de `src/config/coordinates/`:

```
📂 Loaded 2 template(s) for 'nu'
📂 Loaded 1 template(s) for 'bradesco'
```

### 2. Comparação de Estrutura

Para cada arquivo de entrada:

-   Compara a estrutura visual com todos os templates
-   Usa **histogram correlation** + **edge detection**
-   Calcula score de similaridade (0-100%)

### 3. Aplicação de Máscaras

Quando encontra um match (≥75% similaridade):

-   Escala as coordenadas proporcionalmente
-   Aplica tarjas pretas nas posições corretas
-   Salva o arquivo mascarado

## 📊 Formato das Coordenadas

```json
[
    {
        "x": 406,
        "y": 822,
        "width": 386,
        "height": 47
    },
    {
        "x": 580,
        "y": 931,
        "width": 212,
        "height": 53
    }
]
```

Coordenadas em **pixels absolutos** da imagem de referência.

## 📈 Output Exemplo

```
🔍 Processing files from: ./test/

📄 Processing: comprovante_nu_001.jpg
✅ Match found: nu/coordinates_output_a (similarity: 89.5%)
   📏 Scaled coordinates from 828x2786 to 1080x3640
   ✅ Masked file saved to: ./masked_output/comprovante_nu_001_masked.jpg

📄 Processing: comprovante_bradesco_001.jpg
✅ Match found: bradesco/coordinates_output_pix (similarity: 92.3%)
   ✅ Masked file saved to: ./masked_output/comprovante_bradesco_001_masked.jpg

============================================================
📊 Processing Statistics
============================================================
Total files processed: 5
✅ Successfully masked: 4
⚠️  No matching template: 1
❌ Errors: 0
============================================================
```

## 🎯 Vantagens do Sistema

1. **Sem custos de API**: Não usa LLM após configuração inicial
2. **Rápido**: Comparação visual é muito mais rápida que LLM
3. **Consistente**: Mesmas coordenadas para layouts similares
4. **Escalável**: Adicionar novos templates conforme necessário
5. **Auto-escala**: Ajusta coordenadas automaticamente para diferentes resoluções

## 🔍 Threshold de Similaridade

Por padrão, usa **75%** de similaridade mínima. Pode ajustar em:

```python
# src/modules/sensitive_data_masker/gemini.py
match = find_matching_template(file_path, templates, threshold=0.75)
```

## ⚠️ Troubleshooting

### "No matching template found"

-   O layout do comprovante é diferente dos templates existentes
-   Crie um novo template para esse layout
-   Ou ajuste o threshold de similaridade

### "Coordinates scaled incorrectly"

-   Verifique se a imagem de referência (.png) tem a mesma proporção
-   Recrie o template com uma imagem de melhor qualidade

### "Multiple templates matching"

-   O sistema escolhe o template com maior similaridade
-   Considere criar templates mais específicos
