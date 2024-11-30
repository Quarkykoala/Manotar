import React, { useState } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import { Users, AlertTriangle, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useInterval } from '../../hooks/useInterval';
import { useTheme } from '../../contexts/ThemeContext';
import DarkModeToggle from '../../components/DarkModeToggle';

// Mock data - replace with actual API calls
const mockLocationData = [
  { location: 'New York', employeeCount: 1200, mentalHealthScore: 7.2, supportRequests: 45 },
  { location: 'London', employeeCount: 800, mentalHealthScore: 6.8, supportRequests: 38 },
  { location: 'Singapore', employeeCount: 600, mentalHealthScore: 7.5, supportRequests: 25 },
  { location: 'Sydney', employeeCount: 450, mentalHealthScore: 7.8, supportRequests: 18 },
];

const mockTimeData = [
  { hour: '9AM', supportRequests: 12, anxietyMentions: 8 },
  { hour: '11AM', supportRequests: 18, anxietyMentions: 15 },
  { hour: '1PM', supportRequests: 10, anxietyMentions: 7 },
  { hour: '3PM', supportRequests: 22, anxietyMentions: 19 },
  { hour: '5PM', supportRequests: 25, anxietyMentions: 21 },
];

// Add department options
const departments = [
  'All Departments',
  'Engineering',
  'Sales',
  'Marketing',
  'HR',
  'Finance',
  'Operations',
  'IT'
];

// Add keyword tracking data
const keywordOccurrences = [
  { keyword: 'overworked', count: 45, trend: '+15%' },
  { keyword: 'stress', count: 38, trend: '+5%' },
  { keyword: 'burnout', count: 22, trend: '-8%' },
  { keyword: 'anxiety', count: 31, trend: '+12%' },
  { keyword: 'deadline', count: 28, trend: '+3%' },
  { keyword: 'pressure', count: 35, trend: '+7%' },
  { keyword: 'workload', count: 42, trend: '+20%' }
];

interface FilterState {
  startDate: string;
  endDate: string;
  location: string;
  department: string;
  seniority: string;
  timeRange: string;
}

interface DashboardProps {}

// Add interface for department data
interface DepartmentData {
  employeeCount: number;
  mentalHealthScore: number;
  supportRequests: number;
  keywords: { [key: string]: number };
}

// Add interface for department comparison
interface DepartmentComparison {
  department: string;
  employeeCount: number;
  mentalHealthScore: number;
  supportRequests: number;
  riskLevel: 'High' | 'Medium' | 'Low';
  topKeywords: string[];
  trendChange: number;
}

// Update the Dashboard component with real-time updates
const Dashboard: React.FC<DashboardProps> = () => {
  const { darkMode } = useTheme();

  const [filters, setFilters] = useState<FilterState>({
    startDate: '2024-01-01',
    endDate: '2024-03-31',
    location: 'All',
    department: 'All',
    seniority: 'All',
    timeRange: '7d'
  });

  const [metrics] = useState({
    totalEmployees: 3050,
    activeUsers: 2850,
    riskyDepartments: 2,
    averageMentalHealthScore: 7.1,
    supportRequestsToday: 28,
    ongoingSessions: 145
  });

  // Add state for department data
  const [selectedDepartmentData, setSelectedDepartmentData] = useState<DepartmentData | null>(null);

  // Add department comparison data
  const [departmentComparisons, setDepartmentComparisons] = useState<DepartmentComparison[]>([
    {
      department: 'Engineering',
      employeeCount: 120,
      mentalHealthScore: 6.8,
      supportRequests: 45,
      riskLevel: 'High',
      topKeywords: ['overworked', 'deadline', 'stress'],
      trendChange: 15
    },
    {
      department: 'Sales',
      employeeCount: 85,
      mentalHealthScore: 7.2,
      supportRequests: 28,
      riskLevel: 'Medium',
      topKeywords: ['pressure', 'anxiety', 'workload'],
      trendChange: -5
    }
  ]);

  // Add real-time updates
  useInterval(() => {
    updateDepartmentComparisons(filters.department);
  }, 30000);

  // Add loading state for transitions
  const [isLoading, setIsLoading] = useState(false);

  // Enhanced update function with loading state
  const updateDepartmentComparisons = async (department: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      // ... rest of the update logic
    } finally {
      setIsLoading(false);
    }
  };

  // Add interactive chart handlers
  const handleChartClick = (data: any) => {
    console.log('Chart clicked:', data);
    // Add your click handling logic
  };

  // Add chart animations
  const chartAnimation = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.5 }
  };

  // Handle department selection
  const handleDepartmentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const department = e.target.value;
    setFilters({ ...filters, department });
    updateDepartmentComparisons(department);

    if (department === 'All Departments') {
      setSelectedDepartmentData(null);
      return;
    }

    // Filter data for selected department
    const departmentData: DepartmentData = {
      employeeCount: mockLocationData.reduce((acc, curr) => acc + curr.employeeCount, 0),
      mentalHealthScore: mockLocationData.reduce((acc, curr) => acc + curr.mentalHealthScore, 0) / mockLocationData.length,
      supportRequests: mockLocationData.reduce((acc, curr) => acc + curr.supportRequests, 0),
      keywords: keywordOccurrences.reduce((acc, curr) => ({
        ...acc,
        [curr.keyword]: curr.count
      }), {})
    };

    setSelectedDepartmentData(departmentData);
  };

  // Render department details when selected
  const renderDepartmentDetails = () => {
    if (!selectedDepartmentData) return null;

    return (
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {filters.department} Department Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-600">Employee Count</p>
            <p className="text-2xl font-bold">{selectedDepartmentData.employeeCount}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-green-600">Mental Health Score</p>
            <p className="text-2xl font-bold">{selectedDepartmentData.mentalHealthScore.toFixed(1)}/10</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-sm text-purple-600">Support Requests</p>
            <p className="text-2xl font-bold">{selectedDepartmentData.supportRequests}</p>
          </div>
        </div>

        {/* Department Keywords */}
        <div className="mt-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Top Keywords</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(selectedDepartmentData.keywords)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 4)
              .map(([keyword, count]) => (
                <div key={keyword} className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-600">{keyword}</p>
                  <p className="text-xl font-bold text-gray-900">{count}</p>
                </div>
              ))}
          </div>
        </div>
      </div>
    );
  };

  // Add comparison view
  const renderDepartmentComparison = () => {
    return (
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Department Comparison</h3>
          <select
            value={filters.department}
            onChange={handleDepartmentChange}
            className="mt-1 block w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="All">Compare All</option>
            {departments.slice(1).map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mental Health Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Support Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trend
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {departmentComparisons.map((dept) => (
                <tr key={dept.department}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{dept.department}</div>
                    <div className="text-sm text-gray-500">{dept.employeeCount} employees</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`text-sm font-medium ${
                      dept.mentalHealthScore > 7 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {dept.mentalHealthScore.toFixed(1)}/10
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {dept.supportRequests}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      dept.riskLevel === 'High' ? 'bg-red-100 text-red-800' :
                      dept.riskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {dept.riskLevel}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`text-sm font-medium ${
                      dept.trendChange > 0 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {dept.trendChange > 0 ? '↑' : '↓'} {Math.abs(dept.trendChange)}%
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Comparison Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div className="h-80">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Mental Health Score Comparison</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentComparisons}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="mentalHealthScore" fill="#8884d8" name="Mental Health Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="h-80">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Support Requests by Department</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentComparisons}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="supportRequests" fill="#82ca9d" name="Support Requests" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  return (
    <AnimatePresence>
      <motion.div 
        className={`min-h-screen ${darkMode ? 'bg-dark-bg text-dark-text' : 'bg-gray-50 text-gray-900'}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* Header */}
        <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} shadow`}>
          <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <h1 className={`text-3xl font-bold ${darkMode ? 'text-dark-text' : 'text-gray-900'}`}>
              Enterprise Mental Health Analytics
            </h1>
            <DarkModeToggle />
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Department Filter */}
          <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6 mb-6`}>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              <div>
                <label className={`block text-sm font-medium ${
                  darkMode ? 'text-dark-text' : 'text-gray-700'
                }`}>
                  Department
                </label>
                <select
                  value={filters.department}
                  onChange={handleDepartmentChange}
                  className={`mt-1 block w-full rounded-md ${
                    darkMode 
                      ? 'bg-gray-800 border-gray-700 text-dark-text' 
                      : 'border-gray-300 text-gray-900'
                  } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
                >
                  {departments.map((dept) => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className={`block text-sm font-medium ${
                  darkMode ? 'text-dark-text' : 'text-gray-700'
                }`}>
                  Time Range
                </label>
                <select
                  value={filters.timeRange}
                  onChange={(e) => setFilters({ ...filters, timeRange: e.target.value })}
                  className={`mt-1 block w-full rounded-md ${
                    darkMode 
                      ? 'bg-gray-800 border-gray-700 text-dark-text' 
                      : 'border-gray-300 text-gray-900'
                  } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
                >
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                  <option value="90d">Last 90 Days</option>
                  <option value="custom">Custom Range</option>
                </select>
              </div>
            </div>
          </div>

          {/* Department Details */}
          {renderDepartmentDetails()}

          {/* Quick Stats */}
          <div className="grid grid-cols-1 gap-6 mb-6 sm:grid-cols-2 lg:grid-cols-3">
            <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6`}>
              <div className="flex items-center">
                <Users className={`h-8 w-8 ${darkMode ? 'text-blue-400' : 'text-blue-500'}`} />
                <div className="ml-4">
                  <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'}`}>
                    Total Employees
                  </h3>
                  <p className={`mt-2 text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                    {metrics.totalEmployees}
                  </p>
                </div>
              </div>
            </div>
            <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6`}>
              <div className="flex items-center">
                <AlertTriangle className={`h-8 w-8 ${darkMode ? 'text-red-400' : 'text-red-500'}`} />
                <div className="ml-4">
                  <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'}`}>
                    At-Risk Departments
                  </h3>
                  <p className={`mt-2 text-3xl font-bold ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                    {metrics.riskyDepartments}
                  </p>
                </div>
              </div>
            </div>
            <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6`}>
              <div className="flex items-center">
                <TrendingUp className={`h-8 w-8 ${darkMode ? 'text-green-400' : 'text-green-500'}`} />
                <div className="ml-4">
                  <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'}`}>
                    Mental Health Score
                  </h3>
                  <p className={`mt-2 text-3xl font-bold ${darkMode ? 'text-green-400' : 'text-green-600'}`}>
                    {metrics.averageMentalHealthScore}/10
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Keyword Occurrences */}
          <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6 mb-6`}>
            <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'} mb-4`}>
              Keyword Occurrences
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {keywordOccurrences.map((item) => (
                <div key={item.keyword} className={`flex items-center justify-between p-4 ${
                  darkMode ? 'bg-gray-800' : 'bg-gray-50'
                } rounded-lg`}>
                  <div>
                    <p className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                      {item.keyword}
                    </p>
                    <p className={`text-2xl font-bold ${darkMode ? 'text-dark-text' : 'text-gray-900'}`}>
                      {item.count}
                    </p>
                  </div>
                  <div className={`text-sm font-medium ${
                    item.trend.startsWith('+') 
                      ? darkMode ? 'text-green-400' : 'text-green-600'
                      : darkMode ? 'text-red-400' : 'text-red-600'
                  }`}>
                    {item.trend}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Charts Grid */}
          <motion.div 
            className="grid grid-cols-1 gap-6 lg:grid-cols-2"
            {...chartAnimation}
          >
            {/* Location Mental Health Scores */}
            <motion.div 
              className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6`}
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'} mb-4`}>
                Mental Health Scores by Location
              </h3>
              <div className="h-80 relative">
                {isLoading && (
                  <div className="absolute inset-0 bg-white/50 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  </div>
                )}
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart 
                    data={mockLocationData}
                    onClick={handleChartClick}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="location" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="mentalHealthScore" fill="#8884d8" name="Mental Health Score" />
                    <Bar dataKey="supportRequests" fill="#82ca9d" name="Support Requests" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Support Request Patterns */}
            <motion.div 
              className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6`}
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'} mb-4`}>
                Support Request Patterns
              </h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mockTimeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="supportRequests" stroke="#8884d8" name="Support Requests" />
                    <Line type="monotone" dataKey="anxietyMentions" stroke="#82ca9d" name="Anxiety Mentions" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          </motion.div>

          {/* Department-wise Analysis */}
          <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6 mt-6`}>
            <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'} mb-4`}>
              Department-wise Analysis
            </h3>
            <div className="overflow-x-auto">
              <table className={`min-w-full divide-y ${darkMode ? 'divide-gray-700' : 'divide-gray-200'}`}>
                <thead className={darkMode ? 'bg-gray-800' : 'bg-gray-50'}>
                  <tr>
                    <th className={`px-6 py-3 text-left text-xs font-medium ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    } uppercase tracking-wider`}>
                      Department
                    </th>
                    <th className={`px-6 py-3 text-left text-xs font-medium ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    } uppercase tracking-wider`}>
                      Employee Count
                    </th>
                    <th className={`px-6 py-3 text-left text-xs font-medium ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    } uppercase tracking-wider`}>
                      Risk Level
                    </th>
                    <th className={`px-6 py-3 text-left text-xs font-medium ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    } uppercase tracking-wider`}>
                      Top Keywords
                    </th>
                  </tr>
                </thead>
                <tbody className={`${
                  darkMode ? 'bg-dark-card divide-gray-700' : 'bg-white divide-gray-200'
                }`}>
                  {departments.slice(1).map((dept) => (
                    <tr key={dept} className={darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-50'}>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                        darkMode ? 'text-dark-text' : 'text-gray-900'
                      }`}>
                        {dept}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-500 ${
                        darkMode ? 'text-dark-text' : 'text-gray-900'
                      }`}>
                        {Math.floor(Math.random() * 100) + 20}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap ${
                        darkMode ? 'text-dark-text' : 'text-gray-900'
                      }`}>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          Math.random() > 0.5 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {Math.random() > 0.5 ? 'Low' : 'High'}
                        </span>
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-500 ${
                        darkMode ? 'text-dark-text' : 'text-gray-900'
                      }`}>
                        {keywordOccurrences.slice(0, 3).map(k => k.keyword).join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add Department Comparison section */}
          <div className={`${darkMode ? 'bg-dark-card' : 'bg-white'} rounded-lg shadow p-6 mb-6`}>
            <div className="flex justify-between items-center mb-4">
              <h3 className={`text-lg font-medium ${darkMode ? 'text-dark-text' : 'text-gray-900'}`}>
                Department Comparison
              </h3>
              <select
                value={filters.department}
                onChange={handleDepartmentChange}
                className={`mt-1 block w-48 rounded-md ${
                  darkMode 
                    ? 'bg-gray-800 border-gray-700 text-dark-text' 
                    : 'border-gray-300 text-gray-900'
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              >
                <option value="All">Compare All</option>
                {departments.slice(1).map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            <div className="overflow-x-auto">
              <table className={`min-w-full divide-y ${darkMode ? 'divide-gray-700' : 'divide-gray-200'}`}>
                <thead className={darkMode ? 'bg-gray-800' : 'bg-gray-50'}>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Department
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Mental Health Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Support Requests
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trend
                    </th>
                  </tr>
                </thead>
                <tbody className={`${
                  darkMode ? 'bg-dark-card divide-gray-700' : 'bg-white divide-gray-200'
                }`}>
                  {departmentComparisons.map((dept) => (
                    <tr key={dept.department}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{dept.department}</div>
                        <div className="text-sm text-gray-500">{dept.employeeCount} employees</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${
                          dept.mentalHealthScore > 7 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {dept.mentalHealthScore.toFixed(1)}/10
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {dept.supportRequests}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          dept.riskLevel === 'High' ? 'bg-red-100 text-red-800' :
                          dept.riskLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {dept.riskLevel}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${
                          dept.trendChange > 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {dept.trendChange > 0 ? '↑' : '↓'} {Math.abs(dept.trendChange)}%
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Comparison Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div className="h-80">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Mental Health Score Comparison</h4>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={departmentComparisons}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" />
                    <YAxis domain={[0, 10]} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="mentalHealthScore" fill="#8884d8" name="Mental Health Score" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="h-80">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Support Requests by Department</h4>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={departmentComparisons}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="supportRequests" fill="#82ca9d" name="Support Requests" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Dashboard;
