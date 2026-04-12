const express = require('express');
const axios = require('axios');
const cors = require('cors');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Swagger configuration
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Gender Classification API (NestJS-style)',
      version: '1.0.0',
      description: 'A REST API that integrates with the Genderize API to classify names by gender with confidence scoring.',
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
  apis: ['task_nest.js'],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Service
class ClassificationService {
  constructor() {}

  async classifyName(name) {
    // Validate name parameter
    if (!name || name === '') {
      const error = new Error('Missing or empty name parameter');
      error.status = 400;
      error.message = 'Missing or empty name parameter';
      throw error;
    }

    if (typeof name !== 'string') {
      const error = new Error('name is not a string');
      error.status = 422;
      error.message = 'name is not a string';
      throw error;
    }

    try {
      // Call Genderize API
      const genderizeUrl = `https://api.genderize.io/?name=${encodeURIComponent(name)}`;
      const response = await axios.get(genderizeUrl, {
        timeout: 5000,
      });

      const apiData = response.data;

      // Extract data from API response
      const gender = apiData.gender;
      const probability = apiData.probability;
      const count = apiData.count;

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
    } catch (error) {
      // Handle specific error types
      if (error.code === 'ECONNABORTED') {
        const err = new Error('Request to external API timed out');
        err.status = 504;
        throw err;
      }

      if (error.response) {
        const err = new Error('Failed to reach external API');
        err.status = 502;
        throw err;
      }

      if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
        const err = new Error('Failed to reach external API');
        err.status = 502;
        throw err;
      }

      // Generic server error
      const err = new Error('Internal server error');
      err.status = 500;
      throw err;
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
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [error]
 *                 message:
 *                   type: string
 *                   example: "Missing or empty name parameter"
 *       422:
 *         description: Name is not a string
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [error]
 *                 message:
 *                   type: string
 *                   example: "name is not a string"
 *       502:
 *         description: Failed to reach external API
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [error]
 *                 message:
 *                   type: string
 *                   example: "Failed to reach external API"
 *       504:
 *         description: Request to external API timed out
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [error]
 *                 message:
 *                   type: string
 *                   example: "Request to external API timed out"
 */
app.get('/api/classify', async (req, res) => {
  try {
    const { name } = req.query;
    const result = await classificationService.classifyName(name);
    return res.status(200).json(result);
  } catch (error) {
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
app.get('/', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Gender Classification API is running',
  });
});

// Start server
const PORT = process.env.PORT || 3300;
app.listen(PORT, () => {
  console.log(`NestJS-style Server is running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/`);
  console.log(`API endpoint: http://localhost:${PORT}/api/classify?name=john`);
  console.log(`Swagger docs: http://localhost:${PORT}/api-docs`);
});

module.exports = app;
