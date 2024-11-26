---
title: "[NestJS + NextJS] Building Real-Time Collaboration with WebSocket"
date: 2024-11-26 10:00:00 +0900
categories: [NestJS]
tags: [NestJS, NextJS, WebSocket, Real-Time, Markdown]
image: /assets/img/posts/24.11/24.11.26.gif
---

Hi there! 
In this post, I’ll walk you through the process of building a simple **real-time Markdown editor**.
This project leverages NestJS for WebSocket integration and NextJS with markdown-it for Markdown parsing and rendering.

Let’s dive in! 🚀

---

## Step 1. Project Overview

**Objective**:
- A simple project created to practice WebSocket implementation.
- Enable multiple users to collaboratively edit a Markdown document in real time on the same page.

---

## Step 2. Introduction to WebSocket

A WebSocket is a communication protocol that provides full-duplex communication channels over a single TCP connection. It enables real-time, event-driven connection between a client and a server.

#[reference](https://www.pubnub.com/guides/websockets/)

## Step 3. Implementation Process

### 3.1 Backend: WebSocket Server with NestJS

1. **Set up NestJS and Install Dependencies**
    ```bash
    nest new markdown-collab
    npm install @nestjs/websockets @nestjs/platform-socket.io socket.io redis
    npm install --save-dev @types/socket.io
    npm install class-validator class-transformer
    ```

2. **Create a WebSocket Gateway**

    ```typescript
    import {
      WebSocketGateway,
      WebSocketServer,
      OnGatewayConnection,
      OnGatewayDisconnect,
      SubscribeMessage,
      MessageBody,
      ConnectedSocket,
    } from '@nestjs/websockets';
    import { Server, Socket } from 'socket.io';


    @WebSocketGateway({ cors: true })
    export class CollabGateway implements OnGatewayConnection, OnGatewayDisconnect {
      // WebSocket server instance
      @WebSocketServer() server: Server;

        // Map to store document content by document ID
      private documents: Map<string, string> = new Map();

      // Triggered when a client connects to the server
      handleConnection(client: Socket) {
        console.log(`Client connected: ${client.id}`);
      }

      // Triggered when a client disconnects from the server
      handleDisconnect(client: Socket) {
        console.log(`Client disconnected: ${client.id}`);
      }

      // Handle the 'join-document' event, allowing a client to join a specific document room
      @SubscribeMessage('join-document')
      handleJoinDocument(
        @MessageBody() data: { docId: string }, // Extract the document ID from the message body
        @ConnectedSocket() client: Socket, // Access the connected socket
      ) {
        client.join(data.docId); // Join the specified document room
        const content = this.documents.get(data.docId) || ''; // Retrieve the document content or default to an empty string
        client.emit('document-content', { content }); // Send the current document content back to the client
      }

      // Handle the 'edit-document' event, updating the document content and notifying other clients in the same room
      @SubscribeMessage('edit-document')
      handleEditDocument(
        @MessageBody() data: { docId: string; content: string }, // Extract the document ID and new content from the message body
        @ConnectedSocket() client: Socket, // Access the connected socket
      ) {
        this.documents.set(data.docId, data.content); // Update the document content in the Map
        this.server
          .to(data.docId) // Broadcast to all clients in the specified document room
          .emit('document-updated', { content: data.content }); // Notify clients with the updated document content
      }
    }
    ```

### 3.2 Frontend: Real-Time Updates with React

1. **Set up NextJS and Install Dependencies**
    ```bash
    npx create-next-app@latest markdown-editor
    npm install socket.io-client markdown-it
    ```

2. **Initialize WebSocket in React**

    ```tsx
    "use client"

    import React, { useEffect, useState, useRef } from "react"
    import io, { Socket } from "socket.io-client"
    import MarkdownIt from "markdown-it"

    const mdParser = new MarkdownIt()

    const Home: React.FC = () => {
      const [docId] = useState("default-doc")
      const [content, setContent] = useState("")
      const [htmlPreview, setHtmlPreview] = useState("")
      const textareaRef = useRef<HTMLTextAreaElement | null>(null)
      const socketRef = useRef<Socket | null>(null)

      useEffect(() => {
        // Establish a WebSocket connection to the server
        const socket = io("http://localhost:3000")
        socketRef.current = socket

        // Join the default document room
        socket.emit("join-document", { docId })

        // Listen for the initial document content sent by the server
        socket.on("document-content", (data) => {
          setContent(data.content)
          setHtmlPreview(mdParser.render(data.content))
        })

        // Listen for updates to the document from other clients
        socket.on("document-updated", (data) => {
          setContent(data.content)
          setHtmlPreview(mdParser.render(data.content))
        })

        // Clean up the socket connection when the component unmounts
        return () => {
          socket.disconnect()
        }
      }, [docId])

      // Handle content changes in the textarea
      const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newContent = e.target.value
        const renderedHTML = mdParser.render(newContent)
        setContent(newContent)
        setHtmlPreview(renderedHTML)

        // Emit the updated content to the server
        socketRef.current?.emit("edit-document", { docId, content: newContent })
      }

      return (
        <div
          style={{ backgroundColor: "#1e1e1e", height: "100vh", color: "#ffffff" }}
        >
          {/* Top title bar */}
          <div
            style={{
              backgroundColor: "#333333",
              padding: "15px",
              fontSize: "20px",
              fontWeight: "bold",
              color: "#ffffff",
              textAlign: "center",
              borderBottom: "2px solid #444444",
            }}
          >
            hoonapps
          </div>

          {/* Main content area */}
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              height: "calc(100% - 50px)",
            }}
          >
            {/* Markdown input area */}
            <div style={{ position: "relative", width: "50%" }}>
              <textarea
                ref={textareaRef}
                value={content}
                onChange={handleContentChange}
                style={{
                  width: "100%",
                  height: "100%",
                  backgroundColor: "#282c34",
                  color: "#ffffff",
                  border: "none",
                  outline: "none",
                  padding: "15px",
                  fontSize: "16px",
                  fontFamily: "monospace",
                  resize: "none",
                }}
              />
            </div>

            {/* HTML preview area */}
            <div
              className="markdown-preview"
              style={{
                width: "50%",
                height: "100%",
                padding: "15px",
                backgroundColor: "#1e1e1e",
                color: "#d4d4d4",
                overflowY: "scroll",
                fontFamily: "Arial, sans-serif",
                lineHeight: "1.6",
              }}
              dangerouslySetInnerHTML={{ __html: htmlPreview }}
            />
          </div>
        </div>
      )
    }

    export default Home
    ```

---

## Step 4. Execution

- **NestJS**
```bash
npm run start
```

- **NextJS**
```bash
npm run dev
```

---

## Step 5. Testing

- Open two browser windows and load the same document.
- When you edit the Markdown in one window, it will update in real time in the other window.
- The Markdown text will also render as HTML in the right-hand preview pane.

---

# Conclusion

Through this project, I gained a deeper understanding of how WebSocket operates by implementing it in a real-time Markdown editor. Additionally, I explored the underlying principles of how WebSocket works. I encourage you to try building a simple visualization to practice and enhance your understanding as well!

Thank you for reading, and happy blogging! 🚀

## References

- [NestJS GitHub Repository](https://github.com/hoonapps/markdown-collab)
- [NextJS GitHub Repository](https://github.com/hoonapps/markdown-editor)