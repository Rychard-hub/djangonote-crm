// Temporary type declarations for skybridge/server
declare module "skybridge/server" {
  export interface McpServerConfig {
    name: string;
    version: string;
  }

  export interface McpServerOptions {
    auth?: {
      type: string;
      tokenEndpoint: string;
    };
  }

  export interface ToolRegistration {
    name: string;
    description: string;
    inputSchema: any;
    view?: {
      component: any;
    };
    handler: (params: any) => Promise<any>;
  }

  export class McpServer {
    constructor(config: McpServerConfig, options?: McpServerOptions);
    registerTool(tool: ToolRegistration): void;
  }
}
