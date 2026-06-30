FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -q
COPY src ./src
RUN mvn package -DskipTests -q

FROM maven:3.9-eclipse-temurin-21 AS dev
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -q
# src/ is bind-mounted over this in docker-compose.dev.yml. DevTools
# (added in pom.xml) restarts the app when compiled .class files change -
# but it watches *compiled output*, not .java source, so editing a file
# alone won't trigger it. Run `mvn compile` (or let your IDE auto-compile
# on save) against the same mounted source to actually see a reload.
CMD ["mvn", "spring-boot:run"]

FROM eclipse-temurin:21-jre-alpine AS production
WORKDIR /app
COPY --from=build /build/target/analytics-service-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
