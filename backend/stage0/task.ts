import express, { Express, Request, Response, NextFunction } from 'express';
import axios from 'axios';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';

const app: Express = express();

// Middleware
app.use(cors({
  origin: '*',
  credentials: false,
}));
app.use(express.json());

// Explicitly set CORS header
app.use((req: Request, res: Response, next: NextFunction) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Swagger configuration
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Gender Classification API (TypeScript)',
      version: '1.0.0',
      description:
        'A REST API that integrates with the Genderize API to classify names by gender with confidence scoring, built with TypeScript.',
      contact: {
        name: 'API Support',
      },
    },
    servers: [
      {
        url: `http://localhost:${process.env.PORT || 8000}`,
        description: 'Development server',
      },
    ],
  },
  apis: ['task.ts'],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Types
interface GenderizeResponse {
  name: string;
  gender: 'male' | 'female' | null;
  probability: number;
  count: number;
}

interface ClassificationResult {
  status: 'success' | 'error';
  data?: {
    name: string;
    gender: string;
    probability: number;
    sample_size: number;
    is_confident: boolean;
    processed_at: string;
  };
  message?: string;
}

// Service class
class ClassificationService {
  async classifyName(name: string): Promise<ClassificationResult> {
    // Validate name parameter
    if (!name || name === '') {
      throw {
        status: 400,
        message: 'Missing or empty name parameter',
      };
    }

    if (typeof name !== 'string') {
      throw {
        status: 422,
        message: 'name is not a string',
      };
    }

    try {
      // Call Genderize API
      const genderizeUrl = `https://api.genderize.io/?name=${encodeURIComponent(name)}`;
      const response = await axios.get<GenderizeResponse>(genderizeUrl, {
        timeout: 5000,
      });

      const apiData = response.data;

      // Extract data from API response
      const { gender, probability, count } = apiData;

      // Handle edge case: null gender or count = 0
      if (gender === null || count === 0) {
        return {
          status: 'error',
          message: 'No prediction available for the provided name',
        };
      }

      // Compute is_confident: true when probability >= 0.7 AND sample_size >= 100
      const isConfident = probability >= 0.7 && count >= 100;

      // Generate processed_at timestamp (UTC, ISO 8601)
      const processedAt = new Date().toISOString();

      // Return successful response
      return {
        status: 'success',
        data: {
          name: name.toLowerCase(),
          gender: gender,
          probability: probability,
          sample_size: count,
          is_confident: isConfident,
          processed_at: processedAt,
        },
      };
    } catch (error: any) {
      // Handle specific error types
      if (error.code === 'ECONNABORTED') {
        throw {
          status: 504,
          message: 'Request to external API timed out',
        };
      }

      if (error.response) {
        throw {
          status: 502,
          message: 'Failed to reach external API',
        };
      }

      if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
        throw {
          status: 502,
          message: 'Failed to reach external API',
        };
      }

      // Generic server error
      throw {
        status: 500,
        message: 'Internal server error',
      };
    }
  }
}

// Initialize service
const classificationService = new ClassificationService();

/**
 * @swagger
 * /api/classify:
 *   get:
 *     summary: Classify a name by gender
 *     description: Calls the Genderize API using a name query parameter, processes the raw response, and returns a structured result with confidence scoring.
 *     tags:
 *       - Classification
 *     parameters:
 *       - in: query
 *         name: name
 *         required: true
 *         description: The name to classify (must be a non-empty string)
 *         schema:
 *           type: string
 *         example: john
 *     responses:
 *       200:
 *         description: Successful classification or error response
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [success, error]
 *                 data:
 *                   type: object
 *                   properties:
 *                     name:
 *                       type: string
 *                       example: john
 *                     gender:
 *                       type: string
 *                       enum: [male, female]
 *                       example: male
 *                     probability:
 *                       type: number
 *                       format: float
 *                       example: 0.99
 *                     sample_size:
 *                       type: integer
 *                       example: 1234
 *                     is_confident:
 *                       type: boolean
 *                       description: True when probability >= 0.7 AND sample_size >= 100
 *                       example: true
 *                     processed_at:
 *                       type: string
 *                       format: date-time
 *                       example: "2026-04-12T14:30:45Z"
 *                 message:
 *                   type: string
 *                   description: Error message (only present when status is error)
 *       400:
 *         description: Missing or empty name parameter
 *       422:
 *         description: Name is not a string
 *       502:
 *         description: Failed to reach external API
 *       504:
 *         description: Request to external API timed out
 */
app.get('/api/classify', async (req: Request, res: Response) => {
  try {
    const { name } = req.query;
    const result = await classificationService.classifyName(name as string);
    return res.status(200).json(result);
  } catch (error: any) {
    const status = error.status || 500;
    return res.status(status).json({
      status: 'error',
      message: error.message,
    });
  }
});

/**
 * @swagger
 * /:
 *   get:
 *     summary: Health check endpoint
 *     description: Returns the status of the API server
 *     tags:
 *       - Health
 *     responses:
 *       200:
 *         description: Server is running
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: ok
 *                 message:
 *                   type: string
 *                   example: Gender Classification API is running
 */
app.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    message: 'Gender Classification API is running',
  });
});

// Start server
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`TypeScript Server is running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/`);
  console.log(`API endpoint: http://localhost:${PORT}/api/classify?name=john`);
  console.log(`Swagger docs: http://localhost:${PORT}/api-docs`);
});

export default app;
