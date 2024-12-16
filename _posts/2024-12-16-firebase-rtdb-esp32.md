---
title: "Implementing Firebase RTDB Streaming with REST API on ESP32"
date: 2024-12-16 21:00:00 +0900
categories: [ESP32]
tags: [ESP32, RTDB, Firebase, Arduino, REST API, Streaming]
image: /assets/img/firebase.png
---


# Introduction

In this guide, we will learn how to connect to Firebase Realtime Database (RTDB) streaming using the REST API and also how to perform PUT operations with an ESP32.

<!-- Esp32에서 firebase rtdb streaming을 rest api 방식으로 연결 및 Put 하는 방법을 배워 볼 것입니다. -->

---

## Step: 1. Set Up Firebase RTDB
- Go to the [Firebase Console](https://console.firebase.google.com/) and create a project.
- Creating a User and Obtaining UID with Email and Password Authentication.
- Enable the Realtime Database and set basic rules for testing:
  ```json
  {
    "rules": {
      ".read": "auth != null && auth.uid === 'USER_UID'",
      ".write": "auth != null && auth.uid === 'USER_UID'"
    }
  }
  ```
  Update rules for production security.

---

## Step: 2. Set UP api key, email, password, path
```cpp
// api key, auth settings
#define API_KEY "Web_API_KEY"
#define USER_EMAIL "USER_EMAIL"
#define USER_PASSWORD "USER_PASSWORD"

// variable settings
String Version = "1.0.0";

String firebaseHost = "DATABASE_HOST_URL"; // rtdb host url
String firebaseStreamingPath = "DATABASE_STREAMING_PATH_UTL"; // streaming url
String firebasePutPath = "DATABASE_PUT_PATH_UTL"// put url
```

## Step: 3. Code Implementation
#### Include Libraries
```cpp
// library settings
#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
```

#### Firebase authetincate & get id token
```cpp
bool authenticateFirebase(const char* email, const char* password){
    String authUrl = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + String(API_KEY);

    // create JSON Body 
    String requestBody;
    StaticJsonDocument<200> doc;
    doc["email"] = email;
    doc["password"] = password;
    doc["returnSecureToken"] = true;
    serializeJson(doc, requestBody);

    // Connect HTTPS
    authClient.setInsecure();
    if (!authClient.connect("identitytoolkit.googleapis.com", 443)) {
        Serial.println("Connection to Firebase Auth failed!");
        return false;
    }

    authClient.println("POST " + authUrl + " HTTP/1.1");
    authClient.println("Host: identitytoolkit.googleapis.com");
    authClient.println("Content-Type: application/json");
    authClient.println("Content-Length: " + String(requestBody.length()));
    authClient.println();
    authClient.print(requestBody);

    // set Response
    String response = "";
    while (authClient.connected()) {
        if (authClient.available()) {
            response = authClient.readString();
            break;
        }
    }

    // check HTTP Status Code
    if (!response.startsWith("HTTP/1.1 200")) {
        Serial.println("Non-200 HTTP response received:");
        return false;
    }

    // remove Header
    int bodyStartIndex = response.indexOf("\r\n\r\n");
    if (bodyStartIndex != -1) {
        response = response.substring(bodyStartIndex + 4);
    }

    // remove chunked data
    int chunkSizeEndIndex = response.indexOf("\r\n");
    if (chunkSizeEndIndex != -1) {
        response = response.substring(chunkSizeEndIndex + 2);
    }

    // Parsing JSON response
    StaticJsonDocument<500> responseDoc;
    DeserializationError error = deserializeJson(responseDoc, response);
    if (error) {
        Serial.print("JSON parse error: ");
        Serial.println(error.c_str());
        return false;
    }

    if (responseDoc.containsKey("idToken") && responseDoc.containsKey("refreshToken")) {
        firebaseAuth = responseDoc["idToken"].as<String>();
        firebaseRefreshToken = responseDoc["refreshToken"].as<String>();
        tokenExpiryTime = millis() + (responseDoc["expiresIn"].as<unsigned long>() * 1000); 
        Serial.println("ID Token: " + firebaseAuth);
        Serial.println("Refresh Token: " + firebaseRefreshToken);
        return true;
    } else {
        Serial.println("Failed to authenticate. Response:");
        Serial.println(response);
        return false;
    }
}
```

#### refresh Firebase token
```cpp
bool refreshFirebaseToken(){
    String refreshUrl = "https://securetoken.googleapis.com/v1/token?key=" + String(API_KEY);

    // create JSON Body 
    String requestBody;
    StaticJsonDocument<200> doc;
    doc["grant_type"] = "refresh_token";
    doc["refresh_token"] = firebaseRefreshToken;
    serializeJson(doc, requestBody);

    // Connect HTTPS
    authClient.setInsecure();
    if (!authClient.connect("securetoken.googleapis.com", 443)) {
        Serial.println("Connection to Firebase Token Refresh failed!");
        return false;
    }

    authClient.println("POST " + refreshUrl + " HTTP/1.1");
    authClient.println("Host: securetoken.googleapis.com");
    authClient.println("Content-Type: application/json");
    authClient.println("Content-Length: " + String(requestBody.length()));
    authClient.println();
    authClient.print(requestBody);

    // check HTTP Status Code
    if (!response.startsWith("HTTP/1.1 200")) {
        Serial.println("Non-200 HTTP response received:");
        return false;
    }

    // remove Header
    int bodyStartIndex = response.indexOf("\r\n\r\n");
    if (bodyStartIndex != -1) {
        response = response.substring(bodyStartIndex + 4);
    }

    // remove chunked data
    int chunkSizeEndIndex = response.indexOf("\r\n");
    if (chunkSizeEndIndex != -1) {
        response = response.substring(chunkSizeEndIndex + 2);
    }

    // set Response
    String response = "";
    while (authClient.connected()) {
        if (authClient.available()) {
            response = authClient.readString();
            break;
        }
    }

    // Parsing JSON response
    StaticJsonDocument<500> responseDoc;
    DeserializationError error = deserializeJson(responseDoc, response);
    if (error) {
        Serial.print("JSON parse error: ");
        Serial.println(error.c_str());
        return false;
    }

    if (responseDoc.containsKey("id_token")) {
        firebaseAuth = responseDoc["id_token"].as<String>();
        tokenExpiryTime = millis() + (responseDoc["expires_in"].as<unsigned long>() * 1000);
        Serial.println("Refreshed ID Token: " + firebaseAuth);
        return true;
    } else {
        Serial.println("Failed to refresh token. Response:");
        Serial.println(response);
        return false;
    }
}
```

#### Connect to a Firebase Stream

This code establishes a streaming connection to a REST API using the event-stream method.

```cpp
bool connectToFirebaseStream(){
  if (millis() - lastReconnectAttempt < 5000) {
      return false;
  }

  lastReconnectAttempt = millis();

  // Create Firebase stream URL 
  String url = String("https://") + firebaseHost.c_str() + firebaseStreamingPath + "?auth=" + firebaseAuth.c_str();

  // Connect Firebase
  Serial.print("Connecting to Firebase...");
  if (!streamClient.connect(firebaseHost.c_str(), 443)) {
      Serial.println("Connection failed!");
      return false;
  }
  Serial.println("Connected!");

  // Write HTTP streamClient
  streamClient.println("GET " + url + " HTTP/1.1");
  streamClient.println("Host: " + String(firebaseHost.c_str()));
  streamClient.println("Accept: text/event-stream");
  streamClient.println("Connection: keep-alive");
  streamClient.println();

  String locationHeader = ""; 
  while (streamClient.connected()) {
    if (streamClient.available()) {
      String line = streamClient.readStringUntil('\n');
      line.trim(); 

      Serial.print("Line Length: ");
      Serial.println(line.length());
      Serial.print("Raw Line: ");
      Serial.println(line);

      if (line.startsWith("Location: ")) {
          String extractedSubstring = line.substring(10);
          locationHeader = extractedSubstring; 
          locationHeader.trim(); 
          Serial.println("Location Header Found: " + locationHeader);
      }

      if (line == "") {
          break;
      }
    }
  }

  if (!locationHeader.isEmpty()) {
      Serial.println("Redirecting to: " + locationHeader);
      streamClient.stop();
      return connectToRedirectedStream(locationHeader);
  }

  Serial.println("Failed to receive HTTP headers.");
  return false;
}
```

#### Observing Streaming Data

This code observes streaming data.

```cpp
void handleFirebaseStream(){
  while (streamClient.available()) {
    String line = streamClient.readStringUntil('\n');
    line.trim();

    // event
    if (line.startsWith("event:")) {
        String eventType = line.substring(6); 
        eventType.trim();
        Serial.println("Event: " + eventType);
    }

    // data
    if (line.startsWith("data:")) {
      String eventData = line.substring(5);
      eventData.trim();
      Serial.println("Data: " + eventData);

      if (eventData == "null") {
        Serial.println("Keep-alive received.");
        continue;
      }{
        handlePathAndData(eventData);
      }
    }
  }
}
```

#### Putting Data

```cpp
// Firebase PUT Data
bool putData(const String& path, int value){
  WiFiClientSecure putClient;
  putClient.setInsecure();

  String url = String("https://") + firebaseHost.c_str() + path + "?auth=" + firebaseAuth.c_str();

  Serial.print("Connecting to Firebase for PUT...");
  if (!putClient.connect(firebaseHost.c_str(), 443)) {
      Serial.println("Connection failed!");
      return false;
  }
  Serial.println("Connected!");

  String jsonPayload = String(value);

  // Write HTTP PUT 
  putClient.println("PUT " + url + " HTTP/1.1");
  putClient.println("Host: " + String(firebaseHost.c_str()));
  putClient.println("Content-Type: application/json");
  putClient.print("Content-Length: ");
  putClient.println(jsonPayload.length());
  putClient.println("Connection: close");
  putClient.println();
  putClient.println(jsonPayload);

  while (putClient.connected()) {
      String line2 = putClient.readStringUntil('\n');
      line2.trim();
      if (line2.startsWith("HTTP/1.1") && line2.indexOf("200")) {
          Serial.println("Response: " + line2);
          cnt_error = 0;
          return true;
      }
  }

  Serial.println("No response or failed to put data.");
  cnt_error++;
  return false;
}

```


# Conclusion
Today, I learned how to use Firebase RTDB streaming and perform PUT operations with an ESP32 in the Arduino IDE.

Recently, I tried using the FirebaseClient library in the Arduino IDE but kept encountering errors. It seemed to be related to SSL and authentication issues, so I decided to implement the functionality myself. I’m sharing this guide for anyone who might face similar issues and need an alternative solution.


<!-- 오늘은 ESP32 Arduino IDE에서 Firebase RTDB 스트리밍, Put 하는 방법을 배웠습니다.
얼마전에 Arduino ide에서 Firebaseclient library를 사용했는데 계속 에러가 발생했습니다.
SSL 관련 이슈랑 auth 관련 이슈가 생긴것 같아서 직접 구현하는 방식으로 대체했고 이를 필요하신 분들이 있을것 같아서 글을 적겠습니다.  -->


Thank you for reading, and happy blogging! 🚀

## References

- [FirebaseClient Library](https://github.com/mobizt/FirebaseClient/blob/main/examples/RealtimeDatabase/Async/Callback/StreamConcurentcy/StreamConcurentcy.ino)
- [Google Docs](https://firebase.google.com/docs/reference/rest/auth)
- [Code Github](https://github.com/hoonapps/ESP32_Firebase_RestApi_Stream)


