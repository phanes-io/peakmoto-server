FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache zstd wget

WORKDIR /photon

RUN wget -q https://github.com/komoot/photon/releases/download/1.0.1/photon-1.0.1.jar -O photon.jar

EXPOSE 2322

CMD ["java", "-Xmx4g", "-jar", "photon.jar", "serve", "-listen-ip", "0.0.0.0", "-listen-port", "2322"]
