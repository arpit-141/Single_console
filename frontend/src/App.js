import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Set up axios defaults
axios.defaults.headers.common['Authorization'] = 'Bearer admin-token';

// Components
const Header = () => {
  return (
    <header className="bg-gray-900 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">🛡️ Unified Security Console</h1>
        <nav className="space-x-4">
          <a href="/" className="hover:text-blue-400">Dashboard</a>
          <a href="/admin" className="hover:text-blue-400">Admin</a>
          <a href="/users" className="hover:text-blue-400">Users</a>
        </nav>
      </div>
    </header>
  );
};

const ModuleCard = ({ module, applications, onAppClick }) => {
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
    <div className="bg-white rounded-lg shadow-md p-6 m-4">
      <div className={`${moduleColors[module]} text-white p-4 rounded-t-lg mb-4`}>
        <h3 className="text-xl font-bold">{module}</h3>
        <p className="text-sm opacity-90">{moduleDescriptions[module]}</p>
      </div>
      
      <div className="space-y-2">
        {applications.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No applications configured</p>
        ) : (
          applications.map((app) => (
            <div
              key={app.id}
              className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => onAppClick(app)}
            >
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium">{app.app_name}</h4>
                  <p className="text-sm text-gray-600">{app.description || 'No description'}</p>
                </div>
                <div className="text-right">
                  <span className="text-blue-500 hover:text-blue-700">
                    Launch →
                  </span>
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
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      {/* Stats Section */}
      <div className="bg-white border-b">
        <div className="container mx-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-500 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">Total Applications</h3>
              <p className="text-2xl font-bold">{stats.total_applications || 0}</p>
            </div>
            <div className="bg-green-500 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">Active Users</h3>
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
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const AdminPanel = () => {
  const [applications, setApplications] = useState([]);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [showAddApp, setShowAddApp] = useState(false);
  const [showAddUser, setShowAddUser] = useState(false);
  const [defectDojoUsers, setDefectDojoUsers] = useState([]);
  const [defectDojoRoles, setDefectDojoRoles] = useState([]);

  const [newApp, setNewApp] = useState({
    app_name: '',
    module: 'XDR',
    redirect_url: '',
    description: '',
    ip: '',
    username: '',
    password: '',
    api_key: ''
  });

  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    roles: [],
    module_access: [],
    is_admin: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [appsRes, usersRes, rolesRes, dojoUsersRes, dojoRolesRes] = await Promise.all([
        axios.get(`${API}/applications`),
        axios.get(`${API}/users`),
        axios.get(`${API}/roles`),
        axios.get(`${API}/defectdojo/users`),
        axios.get(`${API}/defectdojo/roles`)
      ]);

      setApplications(appsRes.data);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
      setDefectDojoUsers(dojoUsersRes.data.results || []);
      setDefectDojoRoles(dojoRolesRes.data.results || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleAddApp = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/applications`, newApp);
      setNewApp({
        app_name: '',
        module: 'XDR',
        redirect_url: '',
        description: '',
        ip: '',
        username: '',
        password: '',
        api_key: ''
      });
      setShowAddApp(false);
      fetchData();
    } catch (error) {
      console.error('Error adding application:', error);
      alert('Failed to add application');
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/users`, newUser);
      setNewUser({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        roles: [],
        module_access: [],
        is_admin: false
      });
      setShowAddUser(false);
      fetchData();
    } catch (error) {
      console.error('Error adding user:', error);
      alert('Failed to add user');
    }
  };

  const handleDeleteApp = async (appId) => {
    if (window.confirm('Are you sure you want to delete this application?')) {
      try {
        await axios.delete(`${API}/applications/${appId}`);
        fetchData();
      } catch (error) {
        console.error('Error deleting application:', error);
        alert('Failed to delete application');
      }
    }
  };

  const syncDefectDojoRoles = async () => {
    try {
      await axios.post(`${API}/defectdojo/sync-roles`);
      alert('Roles synced successfully');
      fetchData();
    } catch (error) {
      console.error('Error syncing roles:', error);
      alert('Failed to sync roles');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <div className="container mx-auto p-6">
        <h2 className="text-3xl font-bold mb-6">Admin Panel</h2>
        
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
          <div className="space-x-4">
            <button
              onClick={() => setShowAddApp(true)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Add Application
            </button>
            <button
              onClick={() => setShowAddUser(true)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Add User
            </button>
            <button
              onClick={syncDefectDojoRoles}
              className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
            >
              Sync DefectDojo Roles
            </button>
          </div>
        </div>

        {/* Applications Management */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Applications ({applications.length})</h3>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">Name</th>
                  <th className="px-4 py-2 text-left">Module</th>
                  <th className="px-4 py-2 text-left">URL</th>
                  <th className="px-4 py-2 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id} className="border-t">
                    <td className="px-4 py-2">{app.app_name}</td>
                    <td className="px-4 py-2">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                        {app.module}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <a href={app.redirect_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                        {app.redirect_url}
                      </a>
                    </td>
                    <td className="px-4 py-2">
                      <button
                        onClick={() => handleDeleteApp(app.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Users Management */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Users ({users.length})</h3>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">Username</th>
                  <th className="px-4 py-2 text-left">Email</th>
                  <th className="px-4 py-2 text-left">Admin</th>
                  <th className="px-4 py-2 text-left">Modules</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-t">
                    <td className="px-4 py-2">{user.username}</td>
                    <td className="px-4 py-2">{user.email}</td>
                    <td className="px-4 py-2">
                      {user.is_admin ? (
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">Admin</span>
                      ) : (
                        <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">User</span>
                      )}
                    </td>
                    <td className="px-4 py-2">
                      {user.module_access.map((module) => (
                        <span key={module} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm mr-1">
                          {module}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* DefectDojo Integration Status */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">DefectDojo Integration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">DefectDojo Users ({defectDojoUsers.length})</h4>
              <div className="max-h-32 overflow-y-auto">
                {defectDojoUsers.slice(0, 5).map((user) => (
                  <div key={user.id} className="text-sm text-gray-600">
                    {user.username} ({user.email})
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">DefectDojo Roles ({defectDojoRoles.length})</h4>
              <div className="max-h-32 overflow-y-auto">
                {defectDojoRoles.slice(0, 5).map((role) => (
                  <div key={role.id} className="text-sm text-gray-600">
                    {role.name}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Application Modal */}
      {showAddApp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Add New Application</h3>
            <form onSubmit={handleAddApp}>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Application Name"
                  value={newApp.app_name}
                  onChange={(e) => setNewApp({...newApp, app_name: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
                <select
                  value={newApp.module}
                  onChange={(e) => setNewApp({...newApp, module: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                >
                  <option value="XDR">XDR</option>
                  <option value="XDR+">XDR+</option>
                  <option value="OXDR">OXDR</option>
                  <option value="GSOS">GSOS</option>
                </select>
                <input
                  type="url"
                  placeholder="Redirect URL"
                  value={newApp.redirect_url}
                  onChange={(e) => setNewApp({...newApp, redirect_url: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
                <textarea
                  placeholder="Description"
                  value={newApp.description}
                  onChange={(e) => setNewApp({...newApp, description: e.target.value})}
                  className="w-full p-2 border rounded"
                  rows="2"
                />
                <input
                  type="text"
                  placeholder="IP Address (optional)"
                  value={newApp.ip}
                  onChange={(e) => setNewApp({...newApp, ip: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <input
                  type="text"
                  placeholder="Username (optional)"
                  value={newApp.username}
                  onChange={(e) => setNewApp({...newApp, username: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <input
                  type="password"
                  placeholder="Password (optional)"
                  value={newApp.password}
                  onChange={(e) => setNewApp({...newApp, password: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <input
                  type="text"
                  placeholder="API Key (optional)"
                  value={newApp.api_key}
                  onChange={(e) => setNewApp({...newApp, api_key: e.target.value})}
                  className="w-full p-2 border rounded"
                />
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <button
                  type="button"
                  onClick={() => setShowAddApp(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Add Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {showAddUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Add New User</h3>
            <form onSubmit={handleAddUser}>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Username"
                  value={newUser.username}
                  onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
                <input
                  type="text"
                  placeholder="First Name"
                  value={newUser.first_name}
                  onChange={(e) => setNewUser({...newUser, first_name: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <input
                  type="text"
                  placeholder="Last Name"
                  value={newUser.last_name}
                  onChange={(e) => setNewUser({...newUser, last_name: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newUser.is_admin}
                    onChange={(e) => setNewUser({...newUser, is_admin: e.target.checked})}
                    className="mr-2"
                  />
                  <label>Admin User</label>
                </div>
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <button
                  type="button"
                  onClick={() => setShowAddUser(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Add User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [defectDojoUsers, setDefectDojoUsers] = useState([]);

  useEffect(() => {
    fetchUsers();
    fetchDefectDojoUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchDefectDojoUsers = async () => {
    try {
      const response = await axios.get(`${API}/defectdojo/users`);
      setDefectDojoUsers(response.data.results || []);
    } catch (error) {
      console.error('Error fetching DefectDojo users:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <div className="container mx-auto p-6">
        <h2 className="text-3xl font-bold mb-6">User Management</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Local Users */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">Local Users ({users.length})</h3>
            <div className="space-y-2">
              {users.map((user) => (
                <div key={user.id} className="border rounded p-3">
                  <div className="font-medium">{user.username}</div>
                  <div className="text-sm text-gray-600">{user.email}</div>
                  <div className="text-sm">
                    {user.is_admin ? (
                      <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">Admin</span>
                    ) : (
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">User</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* DefectDojo Users */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">DefectDojo Users ({defectDojoUsers.length})</h3>
            <div className="space-y-2">
              {defectDojoUsers.slice(0, 10).map((user) => (
                <div key={user.id} className="border rounded p-3">
                  <div className="font-medium">{user.username}</div>
                  <div className="text-sm text-gray-600">{user.email}</div>
                  <div className="text-sm">
                    {user.is_staff ? (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">Staff</span>
                    ) : (
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">User</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;