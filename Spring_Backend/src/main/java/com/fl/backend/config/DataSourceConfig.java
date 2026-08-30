package com.fl.backend.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.sql.DataSource;
import java.net.URI;

@Configuration
public class DataSourceConfig {

    @Value("${spring.datasource.url:${DB_URL:}}")
    private String rawUrl;

    @Value("${spring.datasource.username:${DB_USERNAME:}}")
    private String username;

    @Value("${spring.datasource.password:${DB_PASSWORD:}}")
    private String password;

    @Value("${spring.datasource.driver-class-name:${DB_DRIVER:}}")
    private String driverClassName;

    @Bean
    @Primary
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();

        String url = rawUrl;
        if (url != null && !url.isEmpty()) {
            // Handle standard postgresql:// or postgres:// URLs by converting to jdbc:postgresql://
            if (url.startsWith("postgres://") || url.startsWith("postgresql://")) {
                try {
                    URI uri = new URI(url);
                    String userInfo = uri.getUserInfo();
                    if (userInfo != null && userInfo.contains(":")) {
                        String[] parts = userInfo.split(":", 2);
                        if (username == null || username.isEmpty()) {
                            username = parts[0];
                        }
                        if (password == null || password.isEmpty()) {
                            password = parts[1];
                        }
                    }
                    int port = uri.getPort() == -1 ? 5432 : uri.getPort();
                    String path = uri.getPath();
                    if (path != null && path.startsWith("/")) {
                        path = path.substring(1);
                    }
                    url = String.format("jdbc:postgresql://%s:%d/%s", uri.getHost(), port, path);
                } catch (Exception e) {
                    if (url.startsWith("postgres://")) {
                        url = "jdbc:postgresql://" + url.substring("postgres://".length());
                    } else if (url.startsWith("postgresql://")) {
                        url = "jdbc:postgresql://" + url.substring("postgresql://".length());
                    }
                }
            }
        }

        config.setJdbcUrl(url);
        if (username != null && !username.isEmpty()) {
            config.setUsername(username);
        }
        if (password != null && !password.isEmpty()) {
            config.setPassword(password);
        }
        if (driverClassName != null && !driverClassName.isEmpty()) {
            config.setDriverClassName(driverClassName);
        }

        return new HikariDataSource(config);
    }
}
