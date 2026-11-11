#!/usr/bin/env bash
# ==============================================================================
# Mirror automático GitHub <-> GitLab para script_inf_cit
#
# Uso:
#   bash mirror_repos.sh
#
# Variables opcionales:
#   GITHUB_USER   (por defecto: BENDER35)
#   GITLAB_USER   (por defecto: se detecta con `glab api user`)
#   GITLAB_HOST   (por defecto: gitlab.com)
#   GITLAB_TOKEN  (opcional; solo si no se usa `glab`/SSH)
#   BRANCH        (por defecto: master)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PROJECT_NAME="${PROJECT_NAME:-script_inf_cit}"
GITHUB_USER="${GITHUB_USER:-BENDER35}"
GITLAB_HOST="${GITLAB_HOST:-gitlab.com}"
GITLAB_USER="${GITLAB_USER:-}"
GITLAB_TOKEN="${GITLAB_TOKEN:-${GL_TOKEN:-}}"
BRANCH="${BRANCH:-master}"

log()  { printf '%s\n' "$*"; }
warn() { printf 'ADVERTENCIA: %s\n' "$*" >&2; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[ -d ".git" ] || die "No se encontró un repositorio Git en $SCRIPT_DIR"

# ------------------------------------------------------------------------------
# Detectar usuario de GitLab
# ------------------------------------------------------------------------------
if [ -z "$GITLAB_USER" ]; then
    if command -v glab >/dev/null 2>&1; then
        GITLAB_USER="$(glab api user 2>/dev/null \
            | python3 -c 'import sys,json; print(json.load(sys.stdin).get("username",""))' 2>/dev/null || true)"
    fi
fi
[ -n "$GITLAB_USER" ] || die "No se pudo determinar GITLAB_USER. Exporta GITLAB_USER=tu_usuario"

log "GitHub: $GITHUB_USER/$PROJECT_NAME"
log "GitLab: $GITLAB_USER/$PROJECT_NAME ($GITLAB_HOST)"

# ------------------------------------------------------------------------------
# Configurar remotes
# ------------------------------------------------------------------------------
if ! git remote get-url origin >/dev/null 2>&1; then
    log "Configurando remote origin (GitHub)..."
    git remote add origin "https://github.com/$GITHUB_USER/$PROJECT_NAME.git"
fi

GITLAB_SSH_URL="git@$GITLAB_HOST:$GITLAB_USER/$PROJECT_NAME.git"
if git remote get-url gitlab >/dev/null 2>&1; then
    git remote set-url gitlab "$GITLAB_SSH_URL"
else
    log "Configurando remote gitlab (SSH)..."
    git remote add gitlab "$GITLAB_SSH_URL"
fi

# ------------------------------------------------------------------------------
# Crear el proyecto en GitLab si no existe
# ------------------------------------------------------------------------------
ENCODED_PATH="$(python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$GITLAB_USER/$PROJECT_NAME")"

crear_proyecto_gitlab() {
    log "Creando proyecto GitLab $GITLAB_USER/$PROJECT_NAME..."
    if command -v glab >/dev/null 2>&1; then
        glab api --method POST projects \
            -f "name=$PROJECT_NAME" \
            -f "path=$PROJECT_NAME" \
            -f "visibility=public" \
            -f "description=Auditoría automatizada del sistema de cita previa de oficinas de empleo (SEPE y CC. AA.)" \
            >/dev/null
    elif [ -n "$GITLAB_TOKEN" ]; then
        curl -fsS --request POST "https://$GITLAB_HOST/api/v4/projects" \
            --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
            --data-urlencode "name=$PROJECT_NAME" \
            --data-urlencode "path=$PROJECT_NAME" \
            --data-urlencode "visibility=public" \
            >/dev/null
    else
        die "No hay glab autenticado ni GITLAB_TOKEN para crear el proyecto GitLab"
    fi
}

if command -v glab >/dev/null 2>&1; then
    if glab api "projects/$ENCODED_PATH" >/dev/null 2>&1; then
        log "El proyecto GitLab ya existe."
    else
        crear_proyecto_gitlab
    fi
elif [ -n "$GITLAB_TOKEN" ]; then
    HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' \
        --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        "https://$GITLAB_HOST/api/v4/projects/$ENCODED_PATH" || true)"
    if [ "$HTTP_CODE" = "200" ]; then
        log "El proyecto GitLab ya existe."
    elif [ "$HTTP_CODE" = "404" ]; then
        crear_proyecto_gitlab
    else
        warn "No se pudo verificar el proyecto GitLab (HTTP $HTTP_CODE); se intentará el push igualmente."
    fi
else
    warn "No se pudo verificar el proyecto GitLab (sin glab ni GITLAB_TOKEN)."
fi

# ------------------------------------------------------------------------------
# Sincronizar
# ------------------------------------------------------------------------------
log "Haciendo push a GitHub ($BRANCH)..."
git push origin "$BRANCH"

log "Haciendo push a GitLab ($BRANCH)..."
git push gitlab "$BRANCH"

# ------------------------------------------------------------------------------
# Verificar el mirror
# ------------------------------------------------------------------------------
log "Verificando que ambos remotos apuntan al mismo commit..."
LOCAL_HASH="$(git rev-parse "$BRANCH")"
ORIGIN_HASH="$(git ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')"
GITLAB_HASH="$(git ls-remote gitlab "refs/heads/$BRANCH" | awk '{print $1}')"

log "  Local : $LOCAL_HASH"
log "  GitHub: $ORIGIN_HASH"
log "  GitLab: $GITLAB_HASH"

if [ "$LOCAL_HASH" = "$ORIGIN_HASH" ] && [ "$LOCAL_HASH" = "$GITLAB_HASH" ]; then
    log "✅ Mirror verificado: GitHub y GitLab están sincronizados con el commit local."
else
    die "El mirror NO está sincronizado. Revisa los hashes anteriores."
fi
