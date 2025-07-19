import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ModuleCard = ({ module, applications, onAppClick, hasAccess }) => {
  const moduleColors = {
    'XDR': 'bg-blue-500',
    'XDR+': 'bg-green-500',
    'OXDR': 'bg-purple-500',
    'GSOS': 'bg-orange-500'
  };

  const moduleDescriptions = {
    'XDR': 'Extended Detection and Response',
    'XDR+': 'Advanced XDR with Enhanced Features',
    'OXDR': 'Open XDR Platform',
    'GSOS': 'Global Security Operations System'
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 m-4 ${!hasAccess ? 'opacity-50' : ''}`}>
      <div className={`${moduleColors[module]} text-white p-4 rounded-t-lg mb-4`}>
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold">{module}</h3>
            <p className="text-sm opacity-90">{moduleDescriptions[module]}</p>
          </div>
          {!hasAccess && (
            <div className="text-xs bg-red-500 px-2 py-1 rounded">
              No Access
            </div>
          )}
        </div>
      </div>
      
      <div className="space-y-2">
        {applications.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No applications configured</p>
        ) : (
          applications.map((app) => (
            <div
              key={app.id}
              className={`border rounded-lg p-3 transition-colors ${
                hasAccess && app.is_active
                  ? 'hover:bg-gray-50 cursor-pointer'
                  : 'cursor-not-allowed opacity-50'
              }`}
              onClick={() => hasAccess && app.is_active && onAppClick(app)}
            >
              <div className="flex justify-between items-center">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{app.app_name}</h4>
                    <span className={`px-2 py-1 rounded text-xs ${
                      app.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {app.app_type}
                    </span>
                    {app.sync_roles && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                        Role Sync
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{app.description || 'No description'}</p>
                  {app.ip && (
                    <p className="text-xs text-gray-500 mt-1">
                      {app.ip}:{app.default_port || 8080}
                    </p>
                  )}
                  {app.last_role_sync && (
                    <p className="text-xs text-gray-400 mt-1">
                      Last sync: {new Date(app.last_role_sync).toLocaleString()}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  {hasAccess && app.is_active ? (
                    <span className="text-blue-500 hover:text-blue-700">
                      Launch →
                    </span>
                  ) : (
                    <span className="text-gray-400">
                      {!hasAccess ? 'No Access' : 'Inactive'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const { hasModuleAccess, isAdmin } = useAuth();

  useEffect(() => {
    fetchApplications();
    fetchStats();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${API}/applications`);
      setApplications(response.data);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleAppClick = (app) => {
    if (app.redirect_url) {
      window.open(app.redirect_url, '_blank');
    } else {
      alert('No redirect URL configured for this application');
    }
  };

  const groupedApps = applications.reduce((acc, app) => {
    if (!acc[app.module]) {
      acc[app.module] = [];
    }
    acc[app.module].push(app);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      {/* Stats Section */}
      <div className="bg-white border-b">
        <div className="container mx-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-blue-500 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">Applications</h3>
              <p className="text-2xl font-bold">{stats.total_applications || 0}</p>
            </div>
            <div className="bg-green-500 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">Users</h3>
              <p className="text-2xl font-bold">{stats.total_users || 0}</p>
            </div>
            <div className="bg-purple-500 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">Roles</h3>
              <p className="text-2xl font-bold">{stats.total_roles || 0}</p>
            </div>
            <div className="bg-orange-500 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">DefectDojo</h3>
              <p className="text-2xl font-bold">{stats.defectdojo_connected ? '✓' : '✗'}</p>
            </div>
            <div className="bg-gray-600 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">Auth Mode</h3>
              <p className="text-sm font-bold capitalize">{stats.auth_type || 'Simple'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Modules Section */}
      <div className="container mx-auto p-4">
        <h2 className="text-2xl font-bold mb-6 text-center">Security Modules</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['XDR', 'XDR+', 'OXDR', 'GSOS'].map((module) => (
            <ModuleCard
              key={module}
              module={module}
              applications={groupedApps[module] || []}
              onAppClick={handleAppClick}
              hasAccess={isAdmin() || hasModuleAccess(module)}
            />
          ))}
        </div>
        
        {applications.length === 0 && (
          <div className="text-center mt-8">
            <div className="text-gray-400 text-6xl mb-4">📱</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No Applications Configured</h3>
            <p className="text-gray-500 mb-4">
              Get started by adding your first security application.
            </p>
            {isAdmin() && (
              <a 
                href="/admin"
                className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition duration-200"
              >
                Add Application
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;