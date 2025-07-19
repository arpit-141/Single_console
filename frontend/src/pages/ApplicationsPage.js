import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ApplicationCard = ({ app, onEdit, onDelete, onSyncRoles, canManage }) => {
  const [syncing, setSyncing] = useState(false);

  const handleSyncRoles = async () => {
    setSyncing(true);
    await onSyncRoles(app.id);
    setSyncing(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-xl font-semibold">{app.app_name}</h3>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              app.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {app.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
              {app.app_type}
            </span>
            <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">
              {app.module}
            </span>
            {app.sync_roles && (
              <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                Role Sync Enabled
              </span>
            )}
          </div>
          <p className="text-gray-600 mb-3">{app.description || 'No description'}</p>
          
          <div className="space-y-1 text-sm text-gray-500">
            {app.ip && (
              <div>📍 {app.ip}:{app.default_port || 'N/A'}</div>
            )}
            <div>🔗 <a href={app.redirect_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              {app.redirect_url}
            </a></div>
            <div>📅 Created: {new Date(app.created_at).toLocaleDateString()}</div>
            {app.last_role_sync && (
              <div>🔄 Last Role Sync: {new Date(app.last_role_sync).toLocaleString()}</div>
            )}
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center pt-4 border-t">
        <button
          onClick={() => window.open(app.redirect_url, '_blank')}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
        >
          Launch Application
        </button>

        <div className="flex space-x-2">
          {app.sync_roles && (
            <button
              onClick={handleSyncRoles}
              disabled={syncing}
              className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 disabled:opacity-50"
            >
              {syncing ? (
                <span className="flex items-center">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                  Syncing...
                </span>
              ) : (
                'Sync Roles'
              )}
            </button>
          )}
          
          {canManage && (
            <>
              <button
                onClick={() => onEdit(app)}
                className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(app.id)}
                className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
              >
                Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const ApplicationsPage = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchApplications();
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

  const handleSyncRoles = async (appId) => {
    try {
      const response = await axios.post(`${API}/applications/${appId}/sync-roles`);
      if (response.data.success) {
        alert(`Successfully synced ${response.data.synced_roles} roles`);
        fetchApplications(); // Refresh to update last_role_sync
      } else {
        alert(`Role sync failed: ${response.data.message}`);
      }
    } catch (error) {
      console.error('Error syncing roles:', error);
      alert('Failed to sync roles. Please try again.');
    }
  };

  const handleDelete = async (appId) => {
    if (window.confirm('Are you sure you want to delete this application?')) {
      try {
        await axios.delete(`${API}/applications/${appId}`);
        fetchApplications();
      } catch (error) {
        console.error('Error deleting application:', error);
        alert('Failed to delete application');
      }
    }
  };

  const filteredApplications = applications.filter(app => {
    if (searchTerm && !app.app_name.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !app.app_type.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    if (filter === 'all') return true;
    if (filter === 'active') return app.is_active;
    if (filter === 'inactive') return !app.is_active;
    if (filter === 'sync') return app.sync_roles;
    return app.module === filter;
  });

  const groupedApplications = filteredApplications.reduce((acc, app) => {
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
      
      <div className="container mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Applications</h1>
          {isAdmin() && (
            <a
              href="/admin"
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
            >
              Manage Applications
            </a>
          )}
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search applications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex gap-2">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Applications</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
                <option value="sync">Role Sync Enabled</option>
                <option value="XDR">XDR Module</option>
                <option value="XDR+">XDR+ Module</option>
                <option value="OXDR">OXDR Module</option>
                <option value="GSOS">GSOS Module</option>
              </select>
            </div>
          </div>
        </div>

        {/* Applications Grid */}
        {Object.keys(groupedApplications).length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No Applications Found</h3>
            <p className="text-gray-500">
              {searchTerm || filter !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'No applications are configured yet.'
              }
            </p>
          </div>
        ) : (
          Object.entries(groupedApplications).map(([module, apps]) => (
            <div key={module} className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                {module} Module ({apps.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {apps.map((app) => (
                  <ApplicationCard
                    key={app.id}
                    app={app}
                    onSyncRoles={handleSyncRoles}
                    onDelete={handleDelete}
                    canManage={isAdmin()}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ApplicationsPage;