import { rest, RestHandler } from 'msw';
import { setupServer } from 'msw/node';
import { TEST_CONFIG } from '../config/test.config';

interface RequestContext {
  delay: (ms: number) => ResponseTransformer;
  json: (data: any) => ResponseTransformer;
}

type ResponseTransformer = any;

export const handlers: RestHandler[] = [
  // Mock login endpoint
  rest.post(`${TEST_CONFIG.API_URL}/hr/login`, (_req, res, ctx: RequestContext) => {
    return res(
      ctx.delay(TEST_CONFIG.MOCK_DELAY),
      ctx.json({
        success: true,
        token: 'mock-jwt-token'
      })
    );
  }),

  // Mock keyword stats endpoint
  rest.get(`${TEST_CONFIG.API_URL}/api/keyword-stats`, (_req, res, ctx: RequestContext) => {
    return res(
      ctx.delay(TEST_CONFIG.MOCK_DELAY),
      ctx.json([
        { keyword: 'stress', total_count: 45 },
        { keyword: 'anxiety', total_count: 32 },
        { keyword: 'workload', total_count: 28 }
      ])
    );
  })
];

export const server = setupServer(...handlers);