# transcendence
Der Nils, Paul und ich machen unseren 42 Abschluss


```mermaid
flowchart LR

    subgraph www
        A[Client]
        AA[Client]
        
    end

    subgraph docker Network
        subgraph web server
            A[Client] -->|API Request| B{Webserve}
            A[Client] -->|Request| B{Webserve}
            AA[Client] -->|API Request| B{Webserve}
            AA[Client] -->|Request| B{Webserve}
            B --> |Request|FF[/Volume /app/Frontend /]
        end

        subgraph Router Main Service
            B --> |API Request|C{Django Router Service}
            C --> T[/Volume /app/Router_Service /]
        end

        subgraph MicroServices Service-To-Service arch
            subgraph AuthService
                C -->|gRPC| D[Auth Service]
                D -->Z[/Volume /app/auth_service /]
                D -.->|OAuth2.0 Request| K[\42Intra/]
            end

            subgraph UserService
                C -->|gRPC| E[UserService]
                E -->Y[/Volume /app/User_Service /]
            end

            subgraph AdminService
                C -->|gRPC| F[Admin Service]
                F -->X[/Volume /app/Admin_Service /]
            end

            subgraph GameService
                C -->|gRPC| G[Game Service]
                G -->W[/Volume /app/Game_Service /]
            end

            subgraph StatService
                C -->|gRPC| H[Stat Service]
                H -->V[/Volume /app/Stat_Service /]
            end

            subgraph ChatService
                C -->|gRPC| I[Chat Service]
                I -->Q[/Volume /app/Chat_Service /]
            end

            subgraph Database
                D -->|Query| J[(DB)]
                E -->|Query| J[(DB)]
                F -->|Query| J[(DB)]
                G -->|Query| J[(DB)]
                H -->|Query| J[(DB)]
                I -->|Query| J[(DB)]
                J -->R[/Volume /app/DB /]
            end
        end

       
    end
```