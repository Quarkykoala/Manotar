// Mock data
const mockDashboardData = {
  total_employees: 2850,
  at_risk_departments: 2,
  mental_health_score: 7.4,
  keyword_occurrences: {
    "stress": { count: 45, trend: "+12%" },
    "anxiety": { count: 32, trend: "+5%" },
    "workload": { count: 28, trend: "-3%" },
    "burnout": { count: 25, trend: "+8%" },
    "depression": { count: 20, trend: "-2%" }
  },
  departments: [
    { name: "Engineering", count: 120, risk_level: "Medium" },
    { name: "Sales", count: 85, risk_level: "Low" },
    { name: "Marketing", count: 45, risk_level: "High" },
    { name: "HR", count: 30, risk_level: "Low" }
  ]
};

const API_BASE_URL = 'http://localhost:5000/api';

export const fetchDashboardData = async (startDate?: Date, endDate?: Date) => {
  // For mock data, filter based on date range
  const filteredData = {
    ...mockDashboardData,
    // Add date filtering logic here
  };
  return Promise.resolve(filteredData);
};

export const fetchDepartmentComparison = async () => {
  // Mock department comparison data
  return Promise.resolve([
    { department: "Engineering", wellbeingScore: 7.2, engagementRate: 85, criticalCases: 3 },
    { department: "Sales", wellbeingScore: 6.8, engagementRate: 78, criticalCases: 5 },
    { department: "Marketing", wellbeingScore: 7.5, engagementRate: 82, criticalCases: 2 },
    { department: "HR", wellbeingScore: 7.8, engagementRate: 90, criticalCases: 1 }
  ]);
};

export const fetchTimeSeriesData = async (startDate?: Date, endDate?: Date) => {
  // Generate mock data based on date range
  const days = Math.floor((endDate?.getTime() ?? 0 - startDate?.getTime() ?? 0) / (1000 * 60 * 60 * 24));
  const data = Array.from({ length: days }, (_, i) => {
    const date = new Date(startDate!);
    date.setDate(date.getDate() + i);
    return {
      date: date.toISOString().split('T')[0],
      mental_health_score: 7 + Math.random(),
      support_requests: Math.floor(Math.random() * 20) + 30
    };
  });
  
  return Promise.resolve(data);
};

export const fetchDepartmentDetails = async (department: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/department/${department}/details`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching department details:', error);
    throw error;
  }
};

export const fetchKeywordStats = async (department?: string, location?: string) => {
  try {
    const params = new URLSearchParams();
    if (department) params.append('department', department);
    if (location) params.append('location', location);
    
    const response = await fetch(`${API_BASE_URL}/keyword-stats?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching keyword stats:', error);
    throw error;
  }
};

// Update the generateMonthData function
const generateMonthData = (date: Date) => {
  const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  
  // Helper function to generate random number with 2 decimal places
  const randomDecimal = (min: number, max: number) => {
    return Number((min + Math.random() * (max - min)).toFixed(2));
  };

  const moodData = [
    { 
      month: `Week 1`, 
      anxiety: randomDecimal(30, 60), 
      depression: randomDecimal(20, 40), 
      stress: randomDecimal(40, 70), 
      wellbeing: randomDecimal(60, 80)
    },
    { 
      month: `Week 2`, 
      anxiety: randomDecimal(30, 60), 
      depression: randomDecimal(20, 40), 
      stress: randomDecimal(40, 70), 
      wellbeing: randomDecimal(60, 80)
    },
    { 
      month: `Week 3`, 
      anxiety: randomDecimal(30, 60), 
      depression: randomDecimal(20, 40), 
      stress: randomDecimal(40, 70), 
      wellbeing: randomDecimal(60, 80)
    },
    { 
      month: `Week 4`, 
      anxiety: randomDecimal(30, 60), 
      depression: randomDecimal(20, 40), 
      stress: randomDecimal(40, 70), 
      wellbeing: randomDecimal(60, 80)
    },
  ];

  return {
    moodData,
    averages: {
      current: {
        anxiety: randomDecimal(35, 45),
        depression: randomDecimal(20, 30),
        stress: randomDecimal(45, 65),
        wellbeing: randomDecimal(65, 75)
      },
      previous: {
        anxiety: randomDecimal(35, 45),
        depression: randomDecimal(20, 30),
        stress: randomDecimal(45, 65),
        wellbeing: randomDecimal(65, 75)
      }
    }
  };
};

// Update the fetch functions
export const fetchMoodData = async (date: Date) => {
  const data = generateMonthData(date);
  return {
    data: data.moodData,
    averages: data.averages
  };
};

export const fetchDepartmentData = async (date: Date) => {
  return Promise.resolve([
    { name: "Engineering", wellbeingScore: Number((7 + Math.random()).toFixed(2)), engagementRate: Math.round(75 + Math.random() * 15) },
    { name: "Sales", wellbeingScore: Number((7 + Math.random()).toFixed(2)), engagementRate: Math.round(75 + Math.random() * 15) },
    { name: "Marketing", wellbeingScore: Number((7 + Math.random()).toFixed(2)), engagementRate: Math.round(75 + Math.random() * 15) },
    { name: "HR", wellbeingScore: Number((7 + Math.random()).toFixed(2)), engagementRate: Math.round(75 + Math.random() * 15) },
  ]);
};

export const fetchWellbeingTrend = async (date: Date) => {
  return Promise.resolve(Array.from({ length: 28 }, (_, i) => ({
    date: `Day ${i + 1}`,
    score: Number((7 + Math.random()).toFixed(2))
  })));
};