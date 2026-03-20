DockerBuild = DOCKER_BUILDKIT=1 docker build --no-cache
DockerPush = docker push
DockerRemoveImage = docker rmi
DockerRun = docker run

# Docker 이미지 이름 및 버전 지정
IMAGE		:= registry.seculayer.com:31500/eyecloudai/asst-codec
VERSION 	:= 3.0
REVISION	:= 2026-asst-R2

# 경로 지정
NAME	:=  asst-codec

CONF_DIR	:= /DATA/workspace/kwj/asst-codec/conf
CONTAINER_CONF_DIR := /eyeCloudAI/app/conf

LOG_DIR		:= /eyeCloudAI/logs
CONTAINER_LOG_DIR := /eyeCloudAI/app/logs
PORT		:= 39997:9997

.PHONY: setEnv build push-image

setEnv:
	@echo "${IMAGE}:${VERSION}-${REVISION}"

build:
	${DockerBuild} -t ${IMAGE}:${VERSION}-${REVISION} \
		--secret id=sshconfig,src="${SSH_CONFIG}" \
		--secret id=gitconfig,src="${SECRET_GITCONFIG}" \
		--secret id=cert,src="${SSL_CERT}" \
		--secret id=privatekey,src="${SSH_PRIVATE_KEY}" \
		--secret id=publickey,src="${SSH_PUBLIC_KEY}" \
		-f Dockerfile .

push-image:
	${DockerPush} ${IMAGE}:${VERSION}-${REVISION}

run:
	${DockerRun} --name ${NAME} \
		-v ${CONF_DIR}:${CONTAINER_CONF_DIR} \
		-v ${LOG_DIR}:${CONTAINER_LOG_DIR} \
		-p ${PORT} \
		-t ${IMAGE}:${VERSION}-${REVISION}
