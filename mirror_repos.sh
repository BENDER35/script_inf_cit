#!/bin/bash
# Script de mirror automático entre GitHub y GitLab
# Ejecutar después de configurar los tokens de acceso

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuración - Estas variables pueden ser exportadas como environment variables antes de ejecutar
GITLAB_TOKEN="${GITLAB_TOKEN:-}"
GITLAB_USER="${GITLAB_USER:-BENDER35}"

# Verificar que estamos en el directorio correcto
if [ ! -d ".git" ]; then
    echo "Error: No se encontró un repositorio Git en $SCRIPT_DIR"
    exit 1
fi

# Configurar remote de GitHub si no existe
if ! git remote | grep -q "^origin$"; then
    echo "Configurando remote de GitHub..."
    git remote add origin https://github.com/$GITLAB_USER/script_inf_cit.git
fi

# Configurar remote de GitLab si no existe
if ! git remote | grep -q "^gitlab$"; then
    if [ -n "$GITLAB_TOKEN" ]; then
        echo "Configurando remote de GitLab..."
        git remote add gitlab "https://oauth2:$GITLAB_TOKEN@gitlab.com/$GITLAB_USER/script_inf_cit.git"
    else
        echo "Advertencia: No se proporcionó GITLAB_TOKEN. Remote de GitLab no configurado."
        echo "Para configurarlo, ejecute: export GITLAB_TOKEN=tu_token_aqui"
        exit 1
    fi
fi

# Hacer push a GitHub (siempre que el origin esté configurado)
echo "Haciendo push a GitHub..."
git push origin master

# Hacer push a GitLab
echo "Haciendo push a GitLab..."
git push gitlab master

echo "¡Mirror completado! Los repositorios de GitHub y GitLab están actualizados."