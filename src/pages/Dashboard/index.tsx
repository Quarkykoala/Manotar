import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis,
  Tooltip, ResponsiveContainer
} from 'recharts';
import { Users, AlertCircle, Heart, MessageSquare, TrendingUp, ArrowUp, ArrowDown } from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  fetchDashboardData, 
  fetchDepartmentComparison,
  fetchTimeSeriesData,
  fetchDepartmentDetails,
  fetchKeywordStats,
  fetchMoodData,
  fetchDepartmentData,
  fetchWellbeingTrend 
} from '@/services/api';
import { KeywordCloud } from '@/components/KeywordCloud';
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorState } from "@/components/ui/error-state";
import { useDataRefresh } from "@/hooks/useDataRefresh";
import { CustomTooltip } from "@/components/CustomTooltip";
import { motion } from "framer-motion";
import { DepartmentView } from '@/components/DepartmentView';
import { MonthNavigator } from '@/components/MonthNavigator';
import { addMonths, subMonths, startOfMonth } from 'date-fns';

// Mock data
const moodData = [
  { month: "Jan", anxiety: 45, depression: 30, stress: 60, wellbeing: 65 },
  { month: "Feb", anxiety: 40, depression: 35, stress: 55, wellbeing: 70 },
  { month: "Mar", anxiety: 50, depression: 25, stress: 65, wellbeing: 60 },
  { month: "Apr", anxiety: 35, depression: 20, stress: 50, wellbeing: 75 },
];

const departmentData = [
  { name: "Engineering", wellbeingScore: 7.2, engagementRate: 85, criticalCases: 3 },
  { name: "Sales", wellbeingScore: 6.8, engagementRate: 78, criticalCases: 5 },
  { name: "Marketing", wellbeingScore: 7.5, engagementRate: 82, criticalCases: 2 },
  { name: "HR", wellbeingScore: 7.8, engagementRate: 90, criticalCases: 1 },
  { name: "Finance", wellbeingScore: 6.9, engagementRate: 75, criticalCases: 4 },
];

const wellbeingTrend = [
  { date: "Mon", score: 7.2 },
  { date: "Tue", score: 7.4 },
  { date: "Wed", score: 7.1 },
  { date: "Thu", score: 7.6 },
  { date: "Fri", score: 7.8 },
];

interface DashboardData {
  total_employees: number;
  at_risk_departments: number;
  mental_health_score: number;
  keyword_occurrences: Record<string, { count: number; trend: string }>;
  departments: Array<{
    name: string;
    count: number;
    risk_level: string;
  }>;
}

export default function Dashboard() {
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [departmentDetails, setDepartmentDetails] = useState<any>(null);
  const [currentMonth, setCurrentMonth] = useState(startOfMonth(new Date()));
  const [moodData, setMoodData] = useState<any[]>([]);
  const [moodTrendMonth, setMoodTrendMonth] = useState(startOfMonth(new Date()));
  const [departmentMonth, setDepartmentMonth] = useState(startOfMonth(new Date()));
  const [wellbeingMonth, setWellbeingMonth] = useState(startOfMonth(new Date()));
  const [departmentChartData, setDepartmentChartData] = useState<any[]>([]);
  const [wellbeingTrend, setWellbeingTrend] = useState<any[]>([]);
  const [departmentStateData, setDepartmentStateData] = useState<any[]>([]);

  const { 
    data: dashboardData, 
    error: dashboardError, 
    isLoading: isDashboardLoading,
    refetch: refetchDashboard 
  } = useDataRefresh(() => fetchDashboardData(), 30000); // Refresh every 30 seconds

  const { 
    data: departmentComparisonData, 
    error: departmentError,
    isLoading: isDepartmentLoading 
  } = useDataRefresh(() => fetchDepartmentComparison(), 30000);

  const { 
    data: timeSeriesData,
    error: timeSeriesError,
    isLoading: isTimeSeriesLoading 
  } = useDataRefresh(() => fetchTimeSeriesData(), 30000);

  const handleDepartmentChange = async (value: string) => {
    setSelectedDepartment(value);
    if (value !== 'all') {
      try {
        const details = await fetchDepartmentDetails(value);
        setDepartmentDetails(details);
      } catch (error) {
        console.error('Error fetching department details:', error);
      }
    } else {
      setDepartmentDetails(null);
    }
  };

  const handlePreviousMonth = async () => {
    const newMonth = subMonths(currentMonth, 1);
    setCurrentMonth(newMonth);
    const newData = await fetchMoodData(newMonth);
    setMoodData(newData);
  };

  const handleNextMonth = async () => {
    const newMonth = addMonths(currentMonth, 1);
    setCurrentMonth(newMonth);
    const newData = await fetchMoodData(newMonth);
    setMoodData(newData);
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [moodResponse, departmentResponse, wellbeingResponse] = await Promise.all([
          fetchMoodData(moodTrendMonth),
          fetchDepartmentData(departmentMonth),
          fetchWellbeingTrend(wellbeingMonth)
        ]);
        setMoodData(moodResponse.data);
        setDepartmentStateData(departmentResponse);
        setWellbeingTrend(wellbeingResponse);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };
    fetchInitialData();
  }, []);

  const handleMoodTrendMonthChange = async (direction: 'prev' | 'next') => {
    const newMonth = direction === 'prev' 
      ? subMonths(moodTrendMonth, 1)
      : addMonths(moodTrendMonth, 1);
    setMoodTrendMonth(newMonth);
    try {
      const response = await fetchMoodData(newMonth);
      console.log('New mood data:', response.data); // Debug log
      setMoodData(response.data);
    } catch (error) {
      console.error('Error fetching mood data:', error);
    }
  };

  const handleDepartmentMonthChange = async (direction: 'prev' | 'next') => {
    const newMonth = direction === 'prev'
      ? subMonths(departmentMonth, 1)
      : addMonths(departmentMonth, 1);
    setDepartmentMonth(newMonth);
    try {
      const data = await fetchDepartmentData(newMonth);
      console.log('New department data:', data);
      setDepartmentStateData(data);
    } catch (error) {
      console.error('Error fetching department data:', error);
    }
  };

  const handleWellbeingMonthChange = async (direction: 'prev' | 'next') => {
    const newMonth = direction === 'prev'
      ? subMonths(wellbeingMonth, 1)
      : addMonths(wellbeingMonth, 1);
    setWellbeingMonth(newMonth);
    try {
      const data = await fetchWellbeingTrend(newMonth);
      console.log('New wellbeing data:', data); // Debug log
      setWellbeingTrend(data);
    } catch (error) {
      console.error('Error fetching wellbeing data:', error);
    }
  };

  if (dashboardError || departmentError || timeSeriesError) {
    return (
      <div className="p-4">
        <ErrorState message="Failed to load dashboard data. Please try again later." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Mental Health Analytics Dashboard</h1>
            <p className="text-muted-foreground">
              Monitor employee mental health and wellbeing trends
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Select defaultValue="all" onValueChange={handleDepartmentChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                <SelectItem value="engineering">Engineering</SelectItem>
                <SelectItem value="sales">Sales</SelectItem>
                <SelectItem value="marketing">Marketing</SelectItem>
                <SelectItem value="finance">Finance</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Metrics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
          {isDashboardLoading ? (
            <LoadingSpinner />
          ) : dashboardData ? (
            <>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dashboardData.total_employees}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Employees Engaged</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">1,024</div>
                  <p className="text-xs text-muted-foreground">+5.2% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Average Wellbeing Score</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">7.4</div>
                  <p className="text-xs text-muted-foreground">+0.2 from last week</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Critical Cases</CardTitle>
                  <AlertCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">15</div>
                  <p className="text-xs text-muted-foreground">-2 from last week</p>
                </CardContent>
              </Card>
            </>
          ) : (
            <ErrorState message="No data available" />
          )}
        </div>

        {/* Charts Grid */}
        <div className="grid gap-4 md:grid-cols-2 mb-6">
          {isDepartmentLoading ? (
            <LoadingSpinner />
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Mood Trends</CardTitle>
                  <CardDescription>Monthly trends in reported moods</CardDescription>
                </CardHeader>
                <CardContent>
                  <MonthNavigator
                    currentDate={moodTrendMonth}
                    onPrevious={() => handleMoodTrendMonthChange('prev')}
                    onNext={() => handleMoodTrendMonthChange('next')}
                    disableNext={moodTrendMonth >= startOfMonth(new Date())}
                  />
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart 
                        data={moodData}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                      >
                        <defs>
                          <linearGradient id="anxiety" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ff9f43" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#ff9f43" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="depression" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ee5253" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#ee5253" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="stress" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#576574" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#576574" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="wellbeing" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#2e86de" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#2e86de" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip content={<CustomTooltip />} />
                        <Area 
                          type="monotone" 
                          dataKey="anxiety" 
                          stroke="#ff9f43" 
                          fillOpacity={1} 
                          fill="url(#anxiety)"
                          strokeWidth={2}
                          animationDuration={1000}
                          animationBegin={0}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="depression" 
                          stroke="#ee5253" 
                          fillOpacity={1} 
                          fill="url(#depression)"
                          strokeWidth={2}
                          animationDuration={1000}
                          animationBegin={200}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="stress" 
                          stroke="#576574" 
                          fillOpacity={1} 
                          fill="url(#stress)"
                          strokeWidth={2}
                          animationDuration={1000}
                          animationBegin={400}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="wellbeing" 
                          stroke="#2e86de" 
                          fillOpacity={1} 
                          fill="url(#wellbeing)"
                          strokeWidth={2}
                          animationDuration={1000}
                          animationBegin={600}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Department Wellbeing</CardTitle>
                  <CardDescription>Wellbeing scores by department</CardDescription>
                </CardHeader>
                <CardContent>
                  <MonthNavigator
                    currentDate={departmentMonth}
                    onPrevious={() => handleDepartmentMonthChange('prev')}
                    onNext={() => handleDepartmentMonthChange('next')}
                    disableNext={departmentMonth >= startOfMonth(new Date())}
                    currentValue={departmentComparisonData?.averages?.current?.wellbeing}
                    previousValue={departmentComparisonData?.averages?.previous?.wellbeing}
                    comparisonFormat="decimal"
                  />
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart 
                        data={departmentStateData}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                      >
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar 
                          dataKey="wellbeingScore" 
                          fill="#2e86de"
                          animationDuration={1000}
                          animationBegin={0}
                        >
                          {departmentStateData.map((entry, index) => (
                            <motion.rect
                              key={`bar-${index}`}
                              whileHover={{
                                y: -5,
                                transition: { duration: 0.2 }
                              }}
                            />
                          ))}
                        </Bar>
                        <Bar 
                          dataKey="engagementRate" 
                          fill="#ff9f43"
                          animationDuration={1000}
                          animationBegin={200}
                        >
                          {departmentStateData.map((entry, index) => (
                            <motion.rect
                              key={`bar-${index}`}
                              whileHover={{
                                y: -5,
                                transition: { duration: 0.2 }
                              }}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Wellbeing Trends and Concerns */}
        <div className="grid gap-4 md:grid-cols-7">
          {isTimeSeriesLoading ? (
            <LoadingSpinner />
          ) : timeSeriesData ? (
            <>
              <Card className="md:col-span-4">
                <CardHeader>
                  <CardTitle>Wellbeing Score Trends</CardTitle>
                  <CardDescription>Daily average wellbeing score</CardDescription>
                </CardHeader>
                <CardContent>
                  <MonthNavigator
                    currentDate={wellbeingMonth}
                    onPrevious={() => handleWellbeingMonthChange('prev')}
                    onNext={() => handleWellbeingMonthChange('next')}
                    disableNext={wellbeingMonth >= startOfMonth(new Date())}
                    currentValue={wellbeingTrend?.[wellbeingTrend.length - 1]?.score}
                    previousValue={wellbeingTrend?.[0]?.score}
                    comparisonFormat="decimal"
                  />
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart 
                        data={wellbeingTrend}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                      >
                        <XAxis dataKey="date" />
                        <YAxis domain={[6.5, 8]} />
                        <Tooltip content={<CustomTooltip />} />
                        <Line 
                          type="monotone" 
                          dataKey="score" 
                          stroke="#2e86de" 
                          strokeWidth={3}
                          dot={false}
                          activeDot={{
                            r: 8,
                            style: { fill: '#2e86de', filter: 'drop-shadow(0 4px 6px rgb(0 0 0 / 0.1))' }
                          }}
                          animationDuration={1000}
                          animationBegin={0}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
              <Card className="md:col-span-3">
                <CardHeader>
                  <CardTitle>Top Mental Health Concerns</CardTitle>
                  <CardDescription>Most discussed issues</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none">Work-related Stress</p>
                        <p className="text-sm text-muted-foreground">38% of conversations</p>
                      </div>
                      <TrendingUp className="h-4 w-4 text-destructive" />
                    </div>
                    <div className="flex items-center">
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none">Anxiety</p>
                        <p className="text-sm text-muted-foreground">29% of conversations</p>
                      </div>
                      <ArrowUp className="h-4 w-4 text-warning" />
                    </div>
                    <div className="flex items-center">
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none">Work-Life Balance</p>
                        <p className="text-sm text-muted-foreground">24% of conversations</p>
                      </div>
                      <ArrowDown className="h-4 w-4 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <ErrorState message="No trend data available" />
          )}
        </div>

        {/* Keyword Cloud */}
        {dashboardData?.keyword_occurrences && (
          <div className="mt-6">
            <KeywordCloud data={dashboardData.keyword_occurrences} />
          </div>
        )}

        {/* Add a manual refresh button */}
        <div className="mt-4 flex justify-end">
          <button
            onClick={refetchDashboard}
            className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90"
          >
            Refresh Data
          </button>
        </div>
      </div>

      {selectedDepartment !== 'all' && departmentDetails && (
        <div className="max-w-7xl mx-auto px-4 py-6">
          <DepartmentView 
            department={selectedDepartment} 
            data={departmentDetails} 
          />
        </div>
      )}
    </div>
  );
}