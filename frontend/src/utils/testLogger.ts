type LogLevel = 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  component: string;
  message: string;
  details?: any;
}

class TestLogger {
  private logs: LogEntry[] = [];

  private log(level: LogLevel, component: string, message: string, details?: any) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      component,
      message,
      details
    };
    
    this.logs.push(entry);
    
    // Log to console with color coding
    const colors = {
      INFO: '\x1b[32m',  // Green
      WARN: '\x1b[33m',  // Yellow
      ERROR: '\x1b[31m', // Red
      DEBUG: '\x1b[36m'  // Cyan
    };
    
    console.log(
      `${colors[level]}[${entry.timestamp}] [${level}] ${component}: ${message}\x1b[0m`,
      details ? `\nDetails: ${JSON.stringify(details, null, 2)}` : ''
    );
  }

  info(component: string, message: string, details?: any) {
    this.log('INFO', component, message, details);
  }

  warn(component: string, message: string, details?: any) {
    this.log('WARN', component, message, details);
  }

  error(component: string, message: string, details?: any) {
    this.log('ERROR', component, message, details);
  }

  debug(component: string, message: string, details?: any) {
    this.log('DEBUG', component, message, details);
  }

  getLogs() {
    return this.logs;
  }

  clearLogs() {
    this.logs = [];
  }
}

export const testLogger = new TestLogger();
