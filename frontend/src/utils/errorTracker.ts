interface TestError {
  id: string;
  type: 'setup' | 'runtime' | 'assertion';
  component: string;
  message: string;
  stack?: string;
  timestamp: Date;
  resolved: boolean;
}

class ErrorTracker {
  private errors: TestError[] = [];
  private static instance: ErrorTracker;

  private constructor() {}

  static getInstance(): ErrorTracker {
    if (!ErrorTracker.instance) {
      ErrorTracker.instance = new ErrorTracker();
    }
    return ErrorTracker.instance;
  }

  trackError(error: Partial<TestError>) {
    const newError: TestError = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: error.type || 'runtime',
      component: error.component || 'unknown',
      message: error.message || 'Unknown error',
      stack: error.stack,
      timestamp: new Date(),
      resolved: false
    };
    this.errors.push(newError);
    this.logError(newError);
  }

  private logError(error: TestError) {
    console.error(`[${error.timestamp.toISOString()}] ${error.type.toUpperCase()} ERROR in ${error.component}:`);
    console.error(`Message: ${error.message}`);
    if (error.stack) {
      console.error('Stack:', error.stack);
    }
    console.error('-------------------');
  }

  getUnresolvedErrors() {
    return this.errors.filter(e => !e.resolved);
  }

  getErrorsByComponent(component: string) {
    return this.errors.filter(e => e.component === component);
  }

  getErrorsByType(type: TestError['type']) {
    return this.errors.filter(e => e.type === type);
  }

  markAsResolved(id: string) {
    const error = this.errors.find(e => e.id === id);
    if (error) {
      error.resolved = true;
    }
  }

  generateReport() {
    const report = {
      total: this.errors.length,
      unresolved: this.getUnresolvedErrors().length,
      byType: {
        setup: this.getErrorsByType('setup').length,
        runtime: this.getErrorsByType('runtime').length,
        assertion: this.getErrorsByType('assertion').length
      },
      byComponent: {} as Record<string, number>
    };

    // Group errors by component
    this.errors.forEach(error => {
      report.byComponent[error.component] = (report.byComponent[error.component] || 0) + 1;
    });

    return report;
  }

  clearErrors() {
    this.errors = [];
  }
}

export const errorTracker = ErrorTracker.getInstance();
