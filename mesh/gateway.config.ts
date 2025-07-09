import {
  defineConfig,
  extractFromHeader,
  createInlineSigningKeyProvider,
} from '@graphql-hive/gateway';

// If you plan to use .env files for local development with Node, you might need to import and configure dotenv:
import * as dotenv from 'dotenv';
dotenv.config(); // This would typically be done at the entry point of your application
 
export const gatewayConfig = defineConfig({
  host: '0.0.0.0',
  port: 4000,
  /**
   * Supergraph configuration.
   * Assuming the gateway service runs from the 'mesh' directory and
   * the supergraph file is in 'mesh/build/supergraph.graphql'.
   */
  supergraph: './build/supergraph.graphql',

  /**
   * JWT Authentication and Authorization.
   */
  jwt: {
    forward: {
      payload: true,
      token: false,
      extensionsFieldName: 'jwt',
    },  
    tokenLookupLocations: [
      extractFromHeader({ name: 'authorization', prefix: 'Bearer' }),
    ],
    signingKeyProviders: [
      createInlineSigningKeyProvider(process.env.SUPABASE_JWT_SECRET as string),
    ],
    tokenVerification: {
      issuer: ['https://gaitofyakycvpwqfoevq.supabase.co/auth/v1'],
      audience: ['authenticated'],
      algorithms: ['HS256'],  // Supabase uses HS256
    },
    reject: {
      missingToken: true,
      invalidToken: true,
    },
  },

  /** Header propagation configuration. */
  propagateHeaders: {
    fromClientToSubgraphs({ request, subgraphName }) {
      // Propagate authentication headers to all subgraphs (Journal and Agent)
      const headers: Record<string, string> = {};
      
      // Always propagate the x-internal-id header if present
      const internalId = request.headers.get('x-internal-id');
      if (internalId) {
        headers['x-internal-id'] = internalId;
      }
      
      // Always propagate the Authorization header if present
      const authorization = request.headers.get('authorization');
      if (authorization) {
        headers['authorization'] = authorization;
      }
      
      console.log(`🔍 Gateway: Propagating headers to ${subgraphName}:`, headers);
      return headers;
    },
  },
  /**
   * CORS configuration.
   * Adjust origins as needed for your Flutter app's development and production URLs.
   */
  cors: {
    origin: '*',
    // Example for more specific origins:
    // origin: ['http://localhost:12345', 'http://localhost:5173', 'https://your-app-domain.com'],
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'x-internal-id'],
  },
  /** Logging configuration */
  logging: 'debug',
});