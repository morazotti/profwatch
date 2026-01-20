# Próximos Passos - ProfWatch

## ✅ O que já está rodando (Status Atual)
- [x] **Automação com Playwright**: Substituição do Selenium por Playwright, permitindo raspagem assíncrona e mais estável.
- [x] **Scrapers Funcionais**: UNESP e Unicamp estão extraindo vagas com sucesso (testado com ~20 resultados).
- [x] **Frontend Moderno**: Interface em `/` com listagem, paginação, modo escuro e filtros dinâmicos.
- [x] **Backend com Cache**: `main.py` entrega resultados instantâneos usando cache em memória.
- [x] **Gestão de Dependências**: Migração para `uv` concluída, facilitando a instalação em novos ambientes.

## 🚀 Próximos Passos (Evolução)
Aqui estão os próximos passos recomendados para a evolução da ferramenta:


## 1. Refinamento dos Scrapers
- [ ] **USP**: Investigar o seletor `#inscricao-sitcon`. O site pode estar usando um iframe ou mudando IDs dinamicamente.
- [ ] **UFSCar**: Ajustar o clique no menu "Em Andamento". Verificar se a navegação por texto puro é estável ou se seletores CSS mais específicos são necessários.
- [ ] **Qualidade dos Dados**: Melhorar a extração da "Área do Conhecimento", que em alguns casos vem como `null` ou contém texto extra desnecessário.

## 2. Persistência de Dados
- [ ] **Banco de Dados**: Implementar o uso de **PostgreSQL** ou **SQLite** (via SQLAlchemy) para armazenar as vagas permanentemente. No momento, usamos apenas um cache em memória.
- [ ] **Histórico**: Permitir que o usuário veja vagas que já foram encerradas (arquivamento).
- [ ] **Diferenciação**: Implementar lógica para identificar vagas novas desde o último scraping e evitar duplicatas.

## 3. Melhorias no Frontend
- [ ] **Notificações**: Adicionar um sistema de alertas (e-mail ou Telegram) quando uma vaga em uma área específica for encontrada.
- [ ] **Favoritos**: Permitir que o usuário "marque" vagas de interesse (salvo no localStorage ou no banco vinculado a um perfil).
- [ ] **Responsividade**: Refinar ainda mais a visualização em dispositivos móveis, talvez usando cards em vez de tabela para telas muito pequenas.

## 4. Infraestrutura e Docker
- [ ] **Dockerização**: Atualizar o `Dockerfile` para incluir as dependências do Playwright de forma estável.
- [ ] **Permissões**: Documentar ou automatizar a correção de permissões da `.venv` quando o projeto é montado como volume no Docker.
- [ ] **CI/CD**: Configurar uma GitHub Action para rodar os scrapers periodicamente e validar que os seletores não quebraram.

## 5. Expansão
- [ ] **Novas Instituições**: Adicionar scrapers para universidades federais (ex: UFABC, UNIFESP) e institutos federais (IFSP).
- [ ] **API Pública**: Documentar o endpoint `/scrape` para que outros serviços possam consumir os dados limpos.
