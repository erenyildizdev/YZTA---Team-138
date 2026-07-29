override SHELL := /bin/bash
override .SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := up
.ONESHELL:
.NOTPARALLEL:

.PHONY: setup up down restart build clean force-clean

ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST değişkeni override edilemez)
endif

override PROJECT_ROOT := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
override PROJECT_BASE_NAME := $(shell basename -- "$(PROJECT_ROOT)" | tr '[:upper:]' '[:lower:]' | sed -E 's/^[^a-z0-9]+//; s/[^a-z0-9_-]+//g')
override PROJECT_PATH_ID := $(shell printf '%s' "$(PROJECT_ROOT)" | sha256sum | cut -c1-12)
override PROJECT_NAME_PREFIX := $(shell printf '%s' "$(PROJECT_BASE_NAME)" | cut -c1-40)
override PROJECT_UNIQUE_NAME := $(PROJECT_NAME_PREFIX)-$(PROJECT_PATH_ID)
override COMPOSE_FILE := $(PROJECT_ROOT)/docker-compose.yml
override ENV_FILE := $(PROJECT_ROOT)/.env
override ENV_EXAMPLE := $(PROJECT_ROOT)/.env.example
override FRONTEND_DIR := $(PROJECT_ROOT)/frontend
override RUN_DIR := $(PROJECT_ROOT)/.run
override MAKE_STATE_DIR := $(PROJECT_ROOT)/.make
override COMPOSE_PROJECT_FILE := $(MAKE_STATE_DIR)/compose-project
override FRONTEND_PID_FILE := $(RUN_DIR)/frontend.pid
override FRONTEND_LOG_FILE := $(RUN_DIR)/frontend.log
override FRONTEND_LOCK_FILE := $(RUN_DIR)/frontend.lock
override PROJECT_LOCK_DIR := /tmp/fikirlab-make-$(shell id -u)
override PROJECT_LOCK_FILE := $(PROJECT_LOCK_DIR)/$(PROJECT_PATH_ID).lock
NO_CACHE ?= 0

ifeq ($(strip $(PROJECT_ROOT)),)
$(error Proje kök dizini güvenli biçimde çözümlenemedi)
endif
ifeq ($(strip $(PROJECT_BASE_NAME)),)
$(error Docker Compose proje adı güvenli biçimde üretilemedi)
endif

override define COMMON_FUNCTIONS
say() {
	printf '%s\n' "$$*"
}

fail() {
	printf 'Hata: %s\n' "$$*" >&2
	exit 1
}

lock_project() {
	command -v flock >/dev/null 2>&1 || fail "flock bulunamadı. Önce make setup çalıştırın."
	local current_uid lock_owner lock_mode
	current_uid="$$(id -u)"

	if [[ ! -e "$(PROJECT_LOCK_DIR)" ]]; then
		if ! mkdir -m 0700 -- "$(PROJECT_LOCK_DIR)" 2>/dev/null \
			&& [[ ! -d "$(PROJECT_LOCK_DIR)" ]]; then
			fail "Güvenli proje lock dizini oluşturulamadı."
		fi
	fi

	[[ -d "$(PROJECT_LOCK_DIR)" && ! -L "$(PROJECT_LOCK_DIR)" ]] \
		|| fail "Proje lock yolu güvenli bir dizin değil."
	lock_owner="$$(stat -c '%u' "$(PROJECT_LOCK_DIR)")"
	lock_mode="$$(stat -c '%a' "$(PROJECT_LOCK_DIR)")"
	[[ "$$lock_owner" == "$$current_uid" && "$$lock_mode" == "700" ]] \
		|| fail "Proje lock dizini mevcut kullanıcıya ait ve mode 700 olmalı."

	if [[ -e "$(PROJECT_LOCK_FILE)" ]]; then
		[[ -f "$(PROJECT_LOCK_FILE)" && ! -L "$(PROJECT_LOCK_FILE)" ]] \
			|| fail "Proje lock dosyası güvenli değil."
		lock_owner="$$(stat -c '%u' "$(PROJECT_LOCK_FILE)")"
		[[ "$$lock_owner" == "$$current_uid" ]] \
			|| fail "Proje lock dosyası mevcut kullanıcıya ait değil."
	fi

	exec 8>>"$(PROJECT_LOCK_FILE)"
	flock -w 600 8 || fail "Başka bir Makefile işlemi devam ediyor."
}

unlock_project() {
	flock -u 8 2>/dev/null || true
	exec 8>&-
}

ensure_env() {
	if [[ -e "$(ENV_FILE)" || -L "$(ENV_FILE)" ]]; then
		[[ -f "$(ENV_FILE)" && ! -L "$(ENV_FILE)" ]] \
			|| fail ".env yolu normal, symlink olmayan bir dosya değil."
		say ".env mevcut; değiştirilmedi."
		return
	fi

	[[ -f "$(ENV_EXAMPLE)" && ! -L "$(ENV_EXAMPLE)" ]] \
		|| fail ".env.example bulunamadı veya güvenli bir dosya değil."
	umask 077
	cp -- "$(ENV_EXAMPLE)" "$(ENV_FILE)"
	say ".env, .env.example üzerinden oluşturuldu."
}

node_version_supported() {
	command -v node >/dev/null 2>&1 || return 1
	local major
	major="$$(node -p 'Number(process.versions.node.split(".")[0])' 2>/dev/null)" || return 1
	[[ "$$major" =~ ^[0-9]+$$ ]] || return 1
	(( major == 22 || major == 24 || major == 26 ))
}

compose_v2_available() {
	command -v docker >/dev/null 2>&1 || return 1
	local version major
	version="$$(docker compose version --short 2>/dev/null)" || return 1
	version="$${version#v}"
	major="$${version%%.*}"
	[[ "$$major" =~ ^[0-9]+$$ ]] || return 1
	(( major >= 2 ))
}

sudo_compose_v2_available() {
	(( EUID != 0 )) || return 1
	command -v sudo >/dev/null 2>&1 || return 1
	local version major
	version="$$(sudo -n docker compose version --short 2>/dev/null \
		|| sudo docker compose version --short 2>/dev/null)" || return 1
	version="$${version#v}"
	major="$${version%%.*}"
	[[ "$$major" =~ ^[0-9]+$$ ]] || return 1
	(( major >= 2 ))
}

require_node_and_npm() {
	command -v node >/dev/null 2>&1 || fail "Node.js bulunamadı. Önce make setup çalıştırın."
	node_version_supported \
		|| fail "Desteklenen Node.js 22, 24 veya 26 gerekir. Önce make setup çalıştırın."
	command -v npm >/dev/null 2>&1 || fail "npm bulunamadı. Önce make setup çalıştırın."
}

install_frontend_dependencies() {
	require_node_and_npm
	if [[ -d "$(FRONTEND_DIR)/node_modules" ]]; then
		say "Frontend bağımlılıkları mevcut."
		return
	fi

	say "Frontend bağımlılıkları kuruluyor..."
	if [[ -f "$(FRONTEND_DIR)/package-lock.json" ]]; then
		(cd "$(FRONTEND_DIR)" && npm ci)
	else
		(cd "$(FRONTEND_DIR)" && npm install)
	fi
}

select_docker() {
	command -v docker >/dev/null 2>&1 || fail "Docker bulunamadı. Önce make setup çalıştırın."
	if ! compose_v2_available && ! sudo_compose_v2_available; then
		fail "Docker Compose v2 bulunamadı. Önce make setup çalıştırın."
	fi

	if compose_v2_available && docker info >/dev/null 2>&1; then
		DOCKER_USE_SUDO=0
		select_compose_project
		return
	fi

	if (( EUID != 0 )) && command -v sudo >/dev/null 2>&1; then
		if sudo_compose_v2_available \
			&& (sudo -n docker info >/dev/null 2>&1 \
				|| sudo docker info >/dev/null 2>&1); then
			DOCKER_USE_SUDO=1
			say "Docker erişimi sudo ile sağlanıyor."
			say "Parolasız kullanım için kullanıcıyı docker grubuna ekleyip yeni terminal açabilirsiniz."
			say "Not: docker grubu root yetkisine eşdeğerdir."
			select_compose_project
			return
		fi
	fi

	fail "Docker daemon'ına erişilemiyor. Docker'ı başlatın veya kullanıcı izinlerini düzeltin."
}

select_docker_for_down() {
	if ! command -v docker >/dev/null 2>&1 \
		|| { ! compose_v2_available && ! sudo_compose_v2_available; }; then
		say "Docker/Compose kurulu değil; durdurulacak Docker servisi yok."
		return 1
	fi

	if compose_v2_available && docker info >/dev/null 2>&1; then
		DOCKER_USE_SUDO=0
		select_compose_project
		return 0
	fi

	local docker_error
	docker_error="$$(docker info 2>&1 || true)"
	case "$$docker_error" in
		*"Cannot connect to the Docker daemon"*|\
		*"Is the docker daemon running"*|\
		*"connection refused"*)
			say "Docker daemon zaten kapalı; Compose durdurma adımı atlandı."
			return 1
			;;
	esac

	if (( EUID != 0 )) && command -v sudo >/dev/null 2>&1 \
		&& sudo_compose_v2_available; then
		local sudo_docker_error
		if sudo_docker_error="$$(sudo -n docker info 2>&1)"; then
			DOCKER_USE_SUDO=1
			select_compose_project
			return 0
		fi
		if sudo_docker_error="$$(sudo docker info 2>&1)"; then
			DOCKER_USE_SUDO=1
			select_compose_project
			return 0
		fi
		case "$$sudo_docker_error" in
			*"Cannot connect to the Docker daemon"*|\
			*"Is the docker daemon running"*|\
			*"connection refused"*)
				say "Docker daemon zaten kapalı; Compose durdurma adımı atlandı."
				return 1
				;;
		esac
	fi

	fail "Docker daemon'ına erişilemiyor; izinleri kontrol edin."
}

docker_cli() {
	if [[ "$${DOCKER_USE_SUDO:-0}" == "1" ]]; then
		sudo -- docker "$$@"
	else
		docker "$$@"
	fi
}

select_compose_project() {
	local current_uid state_owner state_mode marker_tmp
	local legacy_owned=0 legacy_foreign=0 container_id working_dir
	local -a marker_lines=()
	current_uid="$$(id -u)"

	if [[ ! -e "$(MAKE_STATE_DIR)" ]]; then
		if ! mkdir -m 0700 -- "$(MAKE_STATE_DIR)" 2>/dev/null \
			&& [[ ! -d "$(MAKE_STATE_DIR)" ]]; then
			fail "Compose kimlik dizini oluşturulamadı."
		fi
	fi

	[[ -d "$(MAKE_STATE_DIR)" && ! -L "$(MAKE_STATE_DIR)" ]] \
		|| fail "Compose kimlik yolu güvenli bir dizin değil."
	state_owner="$$(stat -c '%u' "$(MAKE_STATE_DIR)")"
	state_mode="$$(stat -c '%a' "$(MAKE_STATE_DIR)")"
	[[ "$$state_owner" == "$$current_uid" && "$$state_mode" == "700" ]] \
		|| fail "Compose kimlik dizini mevcut kullanıcıya ait ve mode 700 olmalı."

	if [[ -e "$(COMPOSE_PROJECT_FILE)" ]]; then
		[[ -f "$(COMPOSE_PROJECT_FILE)" && ! -L "$(COMPOSE_PROJECT_FILE)" ]] \
			|| fail "Compose proje kimlik dosyası güvenli değil."
		state_owner="$$(stat -c '%u' "$(COMPOSE_PROJECT_FILE)")"
		[[ "$$state_owner" == "$$current_uid" ]] \
			|| fail "Compose proje kimlik dosyası mevcut kullanıcıya ait değil."

		mapfile -t marker_lines < "$(COMPOSE_PROJECT_FILE)"
		[[ "$${#marker_lines[@]}" == "2" ]] \
			|| fail "Compose proje kimlik dosyası geçersiz."
		[[ "$${marker_lines[1]}" == "$(PROJECT_ROOT)" ]] \
			|| fail "Compose proje kimliği başka bir checkout'a ait."
		case "$${marker_lines[0]}" in
			"$(PROJECT_BASE_NAME)"|"$(PROJECT_UNIQUE_NAME)")
				ACTIVE_PROJECT_NAME="$${marker_lines[0]}"
				;;
			*)
				fail "Compose proje adı izin verilen kapsam dışında."
				;;
		esac
		return
	fi

	while IFS= read -r container_id; do
		[[ -n "$$container_id" ]] || continue
		working_dir="$$(docker_cli inspect \
			--format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' \
			"$$container_id" 2>/dev/null || true)"
		if [[ "$$working_dir" == "$(PROJECT_ROOT)" ]]; then
			legacy_owned=1
		else
			legacy_foreign=1
		fi
	done < <(docker_cli ps -a \
		--filter "label=com.docker.compose.project=$(PROJECT_BASE_NAME)" \
		--format '{{.ID}}')

	if [[ "$$legacy_owned" == "1" && "$$legacy_foreign" == "0" ]]; then
		ACTIVE_PROJECT_NAME="$(PROJECT_BASE_NAME)"
		say "Bu checkout'un mevcut Compose kaynakları güvenli biçimde benimsendi."
	else
		ACTIVE_PROJECT_NAME="$(PROJECT_UNIQUE_NAME)"
		if docker_cli volume inspect \
			"$(PROJECT_BASE_NAME)_postgres_data" >/dev/null 2>&1; then
			say "Sahibi doğrulanamayan mevcut PostgreSQL volume'u korundu; checkout'a özgü yeni kapsam kullanılacak."
		fi
	fi

	marker_tmp="$(COMPOSE_PROJECT_FILE).tmp.$$$$"
	umask 077
	printf '%s\n%s\n' \
		"$$ACTIVE_PROJECT_NAME" \
		"$(PROJECT_ROOT)" > "$$marker_tmp"
	mv -- "$$marker_tmp" "$(COMPOSE_PROJECT_FILE)"
}

compose() {
	[[ -n "$${ACTIVE_PROJECT_NAME:-}" ]] \
		|| fail "Compose proje kapsamı seçilmedi."
	docker_cli compose \
		--project-name "$$ACTIVE_PROJECT_NAME" \
		--project-directory "$(PROJECT_ROOT)" \
		--file "$(COMPOSE_FILE)" \
		"$$@"
}

assert_compose_checkout_ownership() {
	local container_id working_dir
	while IFS= read -r container_id; do
		[[ -n "$$container_id" ]] || continue
		working_dir="$$(docker_cli inspect \
			--format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' \
			"$$container_id" 2>/dev/null || true)"
		[[ "$$working_dir" == "$(PROJECT_ROOT)" ]] \
			|| fail "Aynı Compose proje adı başka bir checkout tarafından kullanılıyor."
	done < <(docker_cli ps -a \
		--filter "label=com.docker.compose.project=$$ACTIVE_PROJECT_NAME" \
		--format '{{.ID}}')
}

wait_for_db() {
	local container_id health deadline
	container_id="$$(compose ps -q db)"
	[[ -n "$$container_id" ]] || fail "PostgreSQL container kimliği bulunamadı."

	deadline=$$((SECONDS + 60))
	while (( SECONDS < deadline )); do
		health="$$(docker_cli inspect \
			--format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}' \
			"$$container_id" 2>/dev/null || true)"

		case "$$health" in
			healthy)
				say "PostgreSQL hazır."
				return
				;;
			unhealthy)
				compose logs --tail 30 db >&2 || true
				fail "PostgreSQL healthcheck başarısız oldu."
				;;
		esac
		sleep 2
	done

	compose logs --tail 30 db >&2 || true
	fail "PostgreSQL 60 saniye içinde hazır olmadı."
}

build_backend_image() {
	local no_cache="$${1:-0}"
	case "$$no_cache" in
		0|"")
			compose build web
			;;
		1)
			compose build --no-cache web
			;;
		*)
			fail "NO_CACHE yalnızca 0 veya 1 olabilir."
			;;
	esac
}

require_frontend_runtime_tools() {
	local tool
	for tool in setsid flock realpath readlink ps tr grep; do
		command -v "$$tool" >/dev/null 2>&1 \
			|| fail "$$tool bulunamadı. Önce make setup çalıştırın."
	done
}

frontend_start_time() {
	local pid="$$1" stat_line stat_rest
	IFS= read -r stat_line < "/proc/$$pid/stat" || return 1
	stat_rest="$${stat_line##*) }"
	local -a stat_fields=()
	read -r -a stat_fields <<< "$$stat_rest"
	(( $${#stat_fields[@]} >= 20 )) || return 1
	printf '%s\n' "$${stat_fields[19]}"
}

frontend_process_owned() {
	local pid="$$1" expected_start="$$2"
	local current_start pgid expected_cwd actual_cwd cmdline

	[[ "$$pid" =~ ^[1-9][0-9]*$$ ]] || return 1
	[[ "$$expected_start" =~ ^[1-9][0-9]*$$ ]] || return 1
	kill -0 "$$pid" 2>/dev/null || return 1

	current_start="$$(frontend_start_time "$$pid" 2>/dev/null)" || return 1
	[[ "$$current_start" == "$$expected_start" ]] || return 1

	pgid="$$(ps -o pgid= -p "$$pid" 2>/dev/null | tr -d '[:space:]')"
	[[ "$$pgid" == "$$pid" ]] || return 1

	expected_cwd="$$(realpath -e "$(FRONTEND_DIR)")" || return 1
	actual_cwd="$$(readlink -e "/proc/$$pid/cwd" 2>/dev/null)" || return 1
	[[ "$$actual_cwd" == "$$expected_cwd" ]] || return 1

	cmdline="$$(tr '\0' ' ' < "/proc/$$pid/cmdline" 2>/dev/null)" || return 1
	[[ "$$cmdline" == *npm* && "$$cmdline" == *"run dev"* ]]
}

frontend_group_alive() {
	local pgid="$$1"
	[[ "$$pgid" =~ ^[1-9][0-9]*$$ ]] || return 1
	kill -0 -- "-$$pgid" 2>/dev/null
}

terminate_frontend_group() {
	local pid="$$1" expected_start="$$2" already_verified="$${3:-0}"
	local attempt

	if [[ "$$already_verified" != "1" ]]; then
		frontend_process_owned "$$pid" "$$expected_start" || return 1
	fi

	kill -TERM -- "-$$pid" 2>/dev/null || true
	for ((attempt = 0; attempt < 40; attempt++)); do
		frontend_group_alive "$$pid" || return 0
		sleep 0.25
	done

	if frontend_group_alive "$$pid"; then
		say "Frontend zamanında kapanmadı; yalnız doğrulanan process group sonlandırılıyor."
		kill -KILL -- "-$$pid" 2>/dev/null || true
		for ((attempt = 0; attempt < 20; attempt++)); do
			frontend_group_alive "$$pid" || return 0
			sleep 0.1
		done
	fi

	! frontend_group_alive "$$pid"
}

validate_frontend_runtime_file() {
	local runtime_file="$$1" current_uid file_owner file_links
	[[ -e "$$runtime_file" || -L "$$runtime_file" ]] || return 0
	[[ -f "$$runtime_file" && ! -L "$$runtime_file" ]] \
		|| fail "$$runtime_file güvenli bir runtime dosyası değil."
	current_uid="$$(id -u)"
	file_owner="$$(stat -c '%u' "$$runtime_file")"
	file_links="$$(stat -c '%h' "$$runtime_file")"
	[[ "$$file_owner" == "$$current_uid" && "$$file_links" == "1" ]] \
		|| fail "$$runtime_file sahipliği veya hard-link sayısı güvenli değil."
	chmod 0600 -- "$$runtime_file"
}

ensure_frontend_runtime_dir() {
	local current_uid runtime_owner runtime_mode runtime_file
	current_uid="$$(id -u)"
	if [[ ! -e "$(RUN_DIR)" && ! -L "$(RUN_DIR)" ]]; then
		if ! mkdir -m 0700 -- "$(RUN_DIR)" 2>/dev/null \
			&& [[ ! -d "$(RUN_DIR)" ]]; then
			fail "Frontend runtime dizini oluşturulamadı."
		fi
	fi

	[[ -d "$(RUN_DIR)" && ! -L "$(RUN_DIR)" ]] \
		|| fail "Frontend runtime yolu güvenli bir dizin değil."
	runtime_owner="$$(stat -c '%u' "$(RUN_DIR)")"
	[[ "$$runtime_owner" == "$$current_uid" ]] \
		|| fail "Frontend runtime dizini mevcut kullanıcıya ait değil."
	chmod 0700 -- "$(RUN_DIR)"
	runtime_mode="$$(stat -c '%a' "$(RUN_DIR)")"
	[[ "$$runtime_mode" == "700" ]] \
		|| fail "Frontend runtime dizini mode 700 olmalı."

	for runtime_file in \
		"$(FRONTEND_PID_FILE)" \
		"$(FRONTEND_LOG_FILE)" \
		"$(FRONTEND_LOCK_FILE)"; do
		validate_frontend_runtime_file "$$runtime_file"
	done
}

lock_frontend_runtime() {
	ensure_frontend_runtime_dir
	umask 077
	exec 9>>"$(FRONTEND_LOCK_FILE)"
	validate_frontend_runtime_file "$(FRONTEND_LOCK_FILE)"
	flock -w 15 9 || fail "Frontend runtime kilidi alınamadı."
}

unlock_frontend_runtime() {
	flock -u 9 2>/dev/null || true
	exec 9>&-
}

remove_frontend_runtime_files() {
	ensure_frontend_runtime_dir
	rm -f -- \
		"$(FRONTEND_PID_FILE)" \
		"$(FRONTEND_LOG_FILE)" \
		"$(FRONTEND_LOCK_FILE)"
	rmdir -- "$(RUN_DIR)" 2>/dev/null || true
}

read_frontend_record() {
	local extra=""
	FRONTEND_PID=""
	FRONTEND_START_TIME=""
	IFS=' ' read -r FRONTEND_PID FRONTEND_START_TIME extra < "$(FRONTEND_PID_FILE)" \
		|| return 1
	[[ -z "$$extra" ]]
}

start_frontend() {
	require_node_and_npm
	require_frontend_runtime_tools
	lock_frontend_runtime

	if [[ -f "$(FRONTEND_PID_FILE)" ]]; then
		if read_frontend_record \
			&& frontend_process_owned "$$FRONTEND_PID" "$$FRONTEND_START_TIME"; then
			say "Frontend zaten çalışıyor (PID $$FRONTEND_PID)."
			unlock_frontend_runtime
			return
		fi

		say "Stale frontend PID kaydı temizlendi."
		rm -f -- "$(FRONTEND_PID_FILE)"
	fi

	: > "$(FRONTEND_LOG_FILE)"
	local pid="" start_time="" ready=0 ownership_verified=0 attempt
	local pid_tmp="$(FRONTEND_PID_FILE).tmp.$$$$"

	cleanup_partial_frontend_start() {
		local cleanup_failed=0 cleanup_attempt
		if [[ "$$ownership_verified" == "0" && -n "$$pid" ]]; then
			for ((cleanup_attempt = 0; cleanup_attempt < 10; cleanup_attempt++)); do
				kill -0 "$$pid" 2>/dev/null || break
				start_time="$$(frontend_start_time "$$pid" 2>/dev/null || true)"
				if [[ -n "$$start_time" ]] \
					&& frontend_process_owned "$$pid" "$$start_time"; then
					ownership_verified=1
					printf '%s %s\n' "$$pid" "$$start_time" > "$$pid_tmp"
					mv -- "$$pid_tmp" "$(FRONTEND_PID_FILE)"
					break
				fi
				sleep 0.05
			done
		fi

		if [[ "$$ownership_verified" == "1" ]]; then
			terminate_frontend_group "$$pid" "$$start_time" 1 \
				|| cleanup_failed=1
		fi
		rm -f -- "$$pid_tmp"
		if [[ "$$cleanup_failed" == "0" ]]; then
			rm -f -- "$(FRONTEND_PID_FILE)"
		else
			say "Frontend grubu sonlandırılamadı; güvenli yeniden deneme için PID kaydı korundu."
		fi
		unlock_frontend_runtime
	}

	handle_frontend_start_signal() {
		cleanup_partial_frontend_start
		trap - EXIT INT TERM HUP
		exit 130
	}

	trap cleanup_partial_frontend_start EXIT
	trap handle_frontend_start_signal INT TERM HUP

	(
		cd "$(FRONTEND_DIR)"
		exec setsid npm run dev -- \
			--host 127.0.0.1 \
			--port 5173 \
			--strictPort
	) 8>&- 9>&- </dev/null > "$(FRONTEND_LOG_FILE)" 2>&1 &

	pid="$$!"
	for ((attempt = 0; attempt < 60; attempt++)); do
		if ! kill -0 "$$pid" 2>/dev/null; then
			break
		fi

		start_time="$$(frontend_start_time "$$pid" 2>/dev/null || true)"
		if [[ "$$ownership_verified" == "0" && -n "$$start_time" ]] \
			&& frontend_process_owned "$$pid" "$$start_time"; then
			ownership_verified=1
			printf '%s %s\n' "$$pid" "$$start_time" > "$$pid_tmp"
			mv -- "$$pid_tmp" "$(FRONTEND_PID_FILE)"
		fi

		if [[ "$$ownership_verified" == "1" ]]; then
			if ! frontend_group_alive "$$pid"; then
				break
			fi
			if grep -q "Local:" "$(FRONTEND_LOG_FILE)"; then
				ready=1
				break
			fi
		fi
		sleep 0.5
	done

	if [[ "$$ready" == "1" ]]; then
		say "Frontend başlatıldı (PID $$pid)."
		trap - EXIT INT TERM HUP
		unlock_frontend_runtime
		return
	fi

	cleanup_partial_frontend_start
	trap - EXIT INT TERM HUP
	tail -n 30 "$(FRONTEND_LOG_FILE)" >&2 || true
	fail "Frontend başlatılamadı. Ayrıntılar .run/frontend.log dosyasında."
}

stop_frontend() {
	require_frontend_runtime_tools
	lock_frontend_runtime

	if [[ ! -f "$(FRONTEND_PID_FILE)" ]]; then
		say "Frontend zaten kapalı."
		unlock_frontend_runtime
		remove_frontend_runtime_files
		return
	fi

	if read_frontend_record \
		&& frontend_process_owned "$$FRONTEND_PID" "$$FRONTEND_START_TIME"; then
		say "Frontend durduruluyor (PID $$FRONTEND_PID)..."
		if ! terminate_frontend_group \
			"$$FRONTEND_PID" "$$FRONTEND_START_TIME" 1; then
			unlock_frontend_runtime
			fail "Frontend process group sonlandırılamadı; PID kaydı korundu."
		fi
	else
		say "PID kaydı stale veya bu projeye ait değil; hiçbir process sonlandırılmadı."
	fi

	unlock_frontend_runtime
	remove_frontend_runtime_files
}

print_urls() {
	say "Frontend: http://localhost:5173"
	say "Backend:  http://localhost:8000"
}

start_stack() {
	ensure_env
	install_frontend_dependencies
	select_docker
	assert_compose_checkout_ownership
	build_backend_image 0
	compose up -d db
	wait_for_db
	compose run --rm --no-deps -T web python manage.py migrate
	compose up -d web
	start_frontend
	print_urls
}

stop_stack() {
	stop_frontend
	ensure_env
	if ! select_docker_for_down; then
		return
	fi
	assert_compose_checkout_ownership
	compose down --remove-orphans
	say "Docker servisleri durduruldu; volume ve paketler korundu."
}

clean_project() {
	ensure_env
	local root_real frontend_real
	root_real="$$(realpath -e "$(PROJECT_ROOT)")"
	frontend_real="$$(realpath -e "$(FRONTEND_DIR)")"
	[[ "$$root_real" == "$(PROJECT_ROOT)" ]] \
		|| fail "Proje kök yolu beklenen konumla eşleşmiyor."
	[[ ! -L "$(FRONTEND_DIR)" && "$$frontend_real" == "$(FRONTEND_DIR)" ]] \
		|| fail "Frontend dizini güvenli proje yolu değil."
	[[ -d "$(PROJECT_ROOT)/backend" && ! -L "$(PROJECT_ROOT)/backend" ]] \
		|| fail "Backend dizini güvenli proje yolu değil."

	select_docker
	assert_compose_checkout_ownership
	stop_frontend
	compose down --volumes --rmi local --remove-orphans

	rm -rf -- \
		"$(FRONTEND_DIR)/node_modules" \
		"$(FRONTEND_DIR)/dist" \
		"$(RUN_DIR)" \
		"$(PROJECT_ROOT)/.pytest_cache" \
		"$(PROJECT_ROOT)/backend/.pytest_cache"

	find "$(PROJECT_ROOT)/backend" -type f \
		\( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(PROJECT_ROOT)/backend" -depth -type d \
		-name '__pycache__' -empty -delete

	say "Proje kaynakları temizlendi. .env ve kaynak kod korundu."
}

run_as_root() {
	if (( EUID == 0 )); then
		"$$@"
		return
	fi
	command -v sudo >/dev/null 2>&1 || fail "Sistem kurulumu için sudo gerekli."
	sudo -- "$$@"
}

add_package() {
	local candidate="$$1" existing
	for existing in "$${SYSTEM_PACKAGES[@]}"; do
		[[ "$$existing" == "$$candidate" ]] && return
	done
	SYSTEM_PACKAGES+=("$$candidate")
}

apt_package_available() {
	apt-cache show "$$1" 2>/dev/null | grep -q '^Package:'
}

configure_nodesource_repository() {
	local temp_dir
	temp_dir="$$(mktemp -d)"

	curl -fsSL \
		-o "$$temp_dir/nodesource.asc" \
		"https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key"
	gpg --batch --yes --dearmor \
		--output "$$temp_dir/nodesource.gpg" \
		"$$temp_dir/nodesource.asc"
	gpg --show-keys "$$temp_dir/nodesource.gpg" >/dev/null

	printf '%s\n' \
		"deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_24.x nodistro main" \
		> "$$temp_dir/nodesource.list"

	run_as_root install -m 0755 -d /etc/apt/keyrings
	run_as_root install -m 0644 \
		"$$temp_dir/nodesource.gpg" \
		/etc/apt/keyrings/nodesource.gpg
	run_as_root install -m 0644 \
		"$$temp_dir/nodesource.list" \
		/etc/apt/sources.list.d/nodesource.list

	rm -f -- \
		"$$temp_dir/nodesource.asc" \
		"$$temp_dir/nodesource.gpg" \
		"$$temp_dir/nodesource.list"
	rmdir -- "$$temp_dir"
}

configure_docker_repository() {
	local distro_id="$$1" codename="$$2" architecture temp_dir
	architecture="$$(dpkg --print-architecture)"
	temp_dir="$$(mktemp -d)"

	curl -fsSL \
		-o "$$temp_dir/docker.asc" \
		"https://download.docker.com/linux/$$distro_id/gpg"
	gpg --show-keys "$$temp_dir/docker.asc" >/dev/null

	printf '%s\n' \
		"deb [arch=$$architecture signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/$$distro_id $$codename stable" \
		> "$$temp_dir/docker.list"

	run_as_root install -m 0755 -d /etc/apt/keyrings
	run_as_root install -m 0644 \
		"$$temp_dir/docker.asc" \
		/etc/apt/keyrings/docker.asc
	run_as_root install -m 0644 \
		"$$temp_dir/docker.list" \
		/etc/apt/sources.list.d/docker.list

	rm -f -- "$$temp_dir/docker.asc" "$$temp_dir/docker.list"
	rmdir -- "$$temp_dir"
}

install_system_tools() {
	[[ -r /etc/os-release ]] || fail "/etc/os-release bulunamadı; yalnız Ubuntu/Debian desteklenir."
	local distro_id codename
	distro_id="$$(. /etc/os-release && printf '%s' "$${ID:-}")"
	codename="$$(. /etc/os-release && printf '%s' "$${VERSION_CODENAME:-}")"
	case "$$distro_id" in
		ubuntu|debian) ;;
		*) fail "make setup yalnız Ubuntu veya Debian üzerinde sistem paketi kurar." ;;
	esac
	[[ -n "$$codename" ]] || fail "Dağıtım kod adı /etc/os-release içinde bulunamadı."

	SYSTEM_PACKAGES=()
	local need_docker=0 need_compose=0 need_node=0 need_npm=0
	local tool candidate candidate_version

	command -v docker >/dev/null 2>&1 || need_docker=1
	compose_v2_available || need_compose=1
	node_version_supported || need_node=1
	command -v npm >/dev/null 2>&1 || need_npm=1

	command -v setsid >/dev/null 2>&1 || add_package util-linux
	command -v flock >/dev/null 2>&1 || add_package util-linux
	command -v realpath >/dev/null 2>&1 || add_package coreutils
	command -v ps >/dev/null 2>&1 || add_package procps
	command -v curl >/dev/null 2>&1 || add_package curl
	command -v gpg >/dev/null 2>&1 || add_package gnupg
	[[ -f /etc/ssl/certs/ca-certificates.crt ]] || add_package ca-certificates

	if (( $${#SYSTEM_PACKAGES[@]} > 0 || need_docker == 1 \
		|| need_compose == 1 || need_node == 1 || need_npm == 1 )); then
		say "Eksik sistem araçları apt üzerinden kuruluyor..."
		run_as_root apt-get update
		if (( $${#SYSTEM_PACKAGES[@]} > 0 )); then
			run_as_root apt-get install -y "$${SYSTEM_PACKAGES[@]}"
		fi

		if (( need_node == 1 )); then
			say "Node.js 24 LTS imzalı apt deposundan kuruluyor..."
			configure_nodesource_repository
			run_as_root apt-get update
			run_as_root apt-get install -y nodejs
		elif (( need_npm == 1 )); then
			run_as_root apt-get install -y npm
		fi

		if (( need_docker == 1 )); then
			say "Docker ve Compose v2 imzalı resmi apt deposundan kuruluyor..."
			configure_docker_repository "$$distro_id" "$$codename"
			run_as_root apt-get update
			run_as_root apt-get install -y \
				docker-ce \
				docker-ce-cli \
				containerd.io \
				docker-buildx-plugin \
				docker-compose-plugin
		elif (( need_compose == 1 )); then
			candidate=""
			for tool in docker-compose-v2 docker-compose-plugin; do
				if apt_package_available "$$tool"; then
					candidate="$$tool"
					break
				fi
			done

			if [[ -z "$$candidate" ]] \
				&& apt_package_available docker-compose; then
				candidate_version="$$(apt-cache policy docker-compose \
					| awk '/Candidate:/ { print $$2; exit }')"
				if [[ -n "$$candidate_version" \
					&& "$$candidate_version" != "(none)" ]] \
					&& dpkg --compare-versions "$$candidate_version" ge 2; then
					candidate="docker-compose"
				fi
			fi

			if [[ -n "$$candidate" ]]; then
				run_as_root apt-get install -y "$$candidate"
			fi

			if ! compose_v2_available; then
				say "Compose v2, Docker'ın imzalı resmi apt deposundan kuruluyor..."
				configure_docker_repository "$$distro_id" "$$codename"
				run_as_root apt-get update
				run_as_root apt-get install -y docker-compose-plugin
			fi
		fi
	else
		say "Gerekli sistem araçları zaten kurulu."
	fi

	command -v docker >/dev/null 2>&1 || fail "Docker kurulamadı."
	compose_v2_available || fail "Docker Compose v2 kurulamadı."
	require_node_and_npm
	require_frontend_runtime_tools
}

start_docker_daemon() {
	if docker info >/dev/null 2>&1; then
		say "Docker daemon çalışıyor."
		return
	fi

	if (( EUID != 0 )) && command -v sudo >/dev/null 2>&1 \
		&& (sudo -n docker info >/dev/null 2>&1 \
			|| sudo docker info >/dev/null 2>&1); then
		say "Docker daemon çalışıyor; erişim sudo gerektiriyor."
		say "Kalıcı erişim için: sudo usermod -aG docker $$(id -un)"
		say "Ardından yeni terminal açın. Docker grubu root yetkisine eşdeğerdir."
		return
	fi

	say "Docker daemon başlatılıyor..."
	if command -v systemctl >/dev/null 2>&1 \
		&& run_as_root systemctl start docker; then
		:
	elif command -v service >/dev/null 2>&1 \
		&& run_as_root service docker start; then
		:
	else
		fail "Docker daemon systemctl veya service ile başlatılamadı."
	fi

	if ! docker info >/dev/null 2>&1; then
		if (( EUID != 0 )) && command -v sudo >/dev/null 2>&1 \
			&& sudo docker info >/dev/null 2>&1; then
			say "Docker erişimi sudo gerektiriyor."
			say "Kalıcı erişim için: sudo usermod -aG docker $$(id -un)"
			say "Ardından yeni terminal açın. Docker grubu root yetkisine eşdeğerdir."
		else
			fail "Docker daemon başlatıldı ancak erişim doğrulanamadı."
		fi
	fi
}
endef

setup:
	@$(COMMON_FUNCTIONS)
	install_system_tools
	lock_project
	start_docker_daemon
	start_stack
	unlock_project

up:
	@$(COMMON_FUNCTIONS)
	lock_project
	start_stack
	unlock_project

down:
	@$(COMMON_FUNCTIONS)
	lock_project
	stop_stack
	unlock_project

restart:
	@$(COMMON_FUNCTIONS)
	lock_project
	stop_stack
	start_stack
	unlock_project

build:
	@$(COMMON_FUNCTIONS)
	lock_project
	ensure_env
	install_frontend_dependencies
	select_docker
	assert_compose_checkout_ownership
	build_backend_image "$(NO_CACHE)"
	(cd "$(FRONTEND_DIR)" && npm run build)
	say "Docker image ve frontend production build hazırlandı."
	unlock_project

clean:
	@$(COMMON_FUNCTIONS)
	printf '%s\n' \
		"Bu işlem projeye ait Docker container, image, network, volume, veritabanı," \
		"frontend paketleri ve build cache'lerini silecek."
	answer=""
	read -r -p "Devam etmek istiyor musunuz? [y/N] " answer || answer=""
	case "$$answer" in
		y|Y)
			lock_project
			clean_project
			unlock_project
			;;
		*)
			say "Temizlik iptal edildi."
			;;
	esac

force-clean:
	@$(COMMON_FUNCTIONS)
	say "Onaysız proje temizliği başlatılıyor..."
	lock_project
	clean_project
	unlock_project
