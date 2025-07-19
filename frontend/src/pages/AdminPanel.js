import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = () => {
  const [applications, setApplications] = useState([]);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [appTemplates, setAppTemplates] = useState({});
  const [showAddApp, setShowAddApp] = useState(false);
  const [showAddUser, setShowAddUser] = useState(false);
  const [loading, setLoading] = useState(true);

  const [newApp, setNewApp] = useState({
    app_name: '',
    app_type: 'DefectDojo',
    module: 'XDR',
    redirect_url: '',
    description: '',
    ip: '',
    username: '',
    password: '',
    api_key: '',
    default_port: 8080,
    sync_roles: false
  });

  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    roles: [],
    module_access: [],
    is_admin: false
  });

  useEffect(() => {
    fetchData();
    fetchAppTemplates();
  }, []);

  const fetchAppTemplates = async () => {
    try {
      const response = await axios.get(`${API}/app-templates`);
      setAppTemplates(response.data);
    } catch (error) {
      console.error('Error fetching app templates:', error);
    }
  };

  const fetchData = async () => {
    try {
      const [appsRes, usersRes, rolesRes] = await Promise.all([
        axios.get(`${API}/applications`),
        axios.get(`${API}/users`),
        axios.get(`${API}/roles`)
      ]);

      setApplications(appsRes.data);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAppTypeChange = (appType) => {
    const template = appTemplates[appType];
    if (template) {
      setNewApp(prev => ({
        ...prev,
        app_type: appType,
        app_name: template.name,
        description: template.description,
        default_port: template.default_port,
        sync_roles: template.supports_role_sync
      }));
    }
  };

  const handleAddApp = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/applications`, newApp);
      setNewApp({
        app_name: '',
        app_type: 'DefectDojo',
        module: 'XDR',
        redirect_url: '',
        description: '',
        ip: '',
        username: '',
        password: '',
        api_key: '',
        default_port: 8080,
        sync_roles: false
      });
      setShowAddApp(false);
      fetchData();
      alert('Application added successfully!');
    } catch (error) {
      console.error('Error adding application:', error);
      alert('Failed to add application: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/users`, newUser);
      setNewUser({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        roles: [],
        module_access: [],
        is_admin: false
      });
      setShowAddUser(false);
      fetchData();
      alert('User added successfully!');
    } catch (error) {
      console.error('Error adding user:', error);
      alert('Failed to add user: ' + (error.response?.data?.detail || 'Unknown error'));
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

  const handleSyncAppRoles = async (appId) => {
    try {
      const response = await axios.post(`${API}/applications/${appId}/sync-roles`);
      if (response.data.success) {
        alert(`Successfully synced ${response.data.synced_roles} roles from ${response.data.app_name}`);
        fetchData();
      } else {
        alert(`Role sync failed: ${response.data.message}`);
      }
    } catch (error) {
      console.error('Error syncing roles:', error);
      alert('Failed to sync roles');
    }
  };

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
        <h2 className="text-3xl font-bold mb-6">Admin Panel</h2>
        
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setShowAddApp(true)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
            >
              Add Application
            </button>
            <button
              onClick={() => setShowAddUser(true)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition duration-200"
            >
              Add User
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
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Module</th>
                  <th className="px-4 py-2 text-left">Status</th>
                  <th className="px-4 py-2 text-left">Role Sync</th>
                  <th className="px-4 py-2 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id} className="border-t">
                    <td className="px-4 py-2">
                      <div>
                        <div className="font-medium">{app.app_name}</div>
                        <div className="text-sm text-gray-500">
                          <a href={app.redirect_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                            {app.redirect_url}
                          </a>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-2">
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                        {app.app_type}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                        {app.module}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-sm ${
                        app.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {app.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      {app.sync_roles ? (
                        <div>
                          <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">
                            Enabled
                          </span>
                          {app.last_role_sync && (
                            <div className="text-xs text-gray-500 mt-1">
                              Last: {new Date(app.last_role_sync).toLocaleString()}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">Disabled</span>
                      )}
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex space-x-2">
                        {app.sync_roles && (
                          <button
                            onClick={() => handleSyncAppRoles(app.id)}
                            className="text-blue-500 hover:text-blue-700 text-sm"
                          >
                            Sync
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteApp(app.id)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Delete
                        </button>
                      </div>
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
                  <th className="px-4 py-2 text-left">User</th>
                  <th className="px-4 py-2 text-left">Email</th>
                  <th className="px-4 py-2 text-left">Role</th>
                  <th className="px-4 py-2 text-left">Module Access</th>
                  <th className="px-4 py-2 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-t">
                    <td className="px-4 py-2">
                      <div>
                        <div className="font-medium">{user.username}</div>
                        <div className="text-sm text-gray-500">
                          {user.first_name} {user.last_name}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-2">{user.email}</td>
                    <td className="px-4 py-2">
                      {user.is_admin ? (
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">Admin</span>
                      ) : (
                        <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">User</span>
                      )}
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex flex-wrap gap-1">
                        {user.module_access.map((module) => (
                          <span key={module} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                            {module}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-sm ${
                        user.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Roles Management */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Roles ({roles.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roles.map((role) => (
              <div key={role.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{role.name}</h4>
                  {role.is_synced && (
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                      Synced
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-2">{role.description}</p>
                {role.app_type && (
                  <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                    {role.app_type}
                  </span>
                )}
                <div className="mt-2">
                  <div className="text-xs text-gray-500">
                    Permissions: {role.permissions.join(', ')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Add Application Modal */}
      {showAddApp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold mb-4">Add New Application</h3>
            <form onSubmit={handleAddApp}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Module</label>
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
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Application Type</label>
                  <select
                    value={newApp.app_type}
                    onChange={(e) => handleAppTypeChange(e.target.value)}
                    className="w-full p-2 border rounded"
                    required
                  >
                    {Object.keys(appTemplates).map(type => (
                      <option key={type} value={type}>{appTemplates[type].name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Application Name</label>
                  <input
                    type="text"
                    placeholder="Application Name"
                    value={newApp.app_name}
                    onChange={(e) => setNewApp({...newApp, app_name: e.target.value})}
                    className="w-full p-2 border rounded"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Redirect URL</label>
                  <input
                    type="url"
                    placeholder="https://your-app.com"
                    value={newApp.redirect_url}
                    onChange={(e) => setNewApp({...newApp, redirect_url: e.target.value})}
                    className="w-full p-2 border rounded"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    placeholder="Application description"
                    value={newApp.description}
                    onChange={(e) => setNewApp({...newApp, description: e.target.value})}
                    className="w-full p-2 border rounded"
                    rows="2"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">IP Address</label>
                    <input
                      type="text"
                      placeholder="192.168.1.100"
                      value={newApp.ip}
                      onChange={(e) => setNewApp({...newApp, ip: e.target.value})}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Port</label>
                    <input
                      type="number"
                      placeholder="8080"
                      value={newApp.default_port}
                      onChange={(e) => setNewApp({...newApp, default_port: parseInt(e.target.value) || 8080})}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                  <input
                    type="text"
                    placeholder="Username (optional)"
                    value={newApp.username}
                    onChange={(e) => setNewApp({...newApp, username: e.target.value})}
                    className="w-full p-2 border rounded"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <input
                    type="password"
                    placeholder="Password (optional)"
                    value={newApp.password}
                    onChange={(e) => setNewApp({...newApp, password: e.target.value})}
                    className="w-full p-2 border rounded"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                  <input
                    type="text"
                    placeholder="API Key (optional)"
                    value={newApp.api_key}
                    onChange={(e) => setNewApp({...newApp, api_key: e.target.value})}
                    className="w-full p-2 border rounded"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="sync_roles"
                    checked={newApp.sync_roles}
                    onChange={(e) => setNewApp({...newApp, sync_roles: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="sync_roles" className="text-sm text-gray-700">
                    Enable role synchronization
                  </label>
                </div>
                
                {/* Show template info */}
                {appTemplates[newApp.app_type] && (
                  <div className="bg-blue-50 p-3 rounded">
                    <p className="text-sm text-blue-800">
                      <strong>Template Info:</strong> {appTemplates[newApp.app_type].description}
                    </p>
                    <p className="text-sm text-blue-600">
                      Default Port: {appTemplates[newApp.app_type].default_port} | 
                      Auth: {appTemplates[newApp.app_type].auth_type} |
                      Role Sync: {appTemplates[newApp.app_type].supports_role_sync ? 'Supported' : 'Not Supported'}
                    </p>
                  </div>
                )}
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
                  type="password"
                  placeholder="Password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  className="w-full p-2 border rounded"
                  minLength="6"
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
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Module Access</label>
                  {['XDR', 'XDR+', 'OXDR', 'GSOS'].map(module => (
                    <label key={module} className="flex items-center mb-1">
                      <input
                        type="checkbox"
                        checked={newUser.module_access.includes(module)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewUser({...newUser, module_access: [...newUser.module_access, module]});
                          } else {
                            setNewUser({...newUser, module_access: newUser.module_access.filter(m => m !== module)});
                          }
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm">{module}</span>
                    </label>
                  ))}
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newUser.is_admin}
                    onChange={(e) => setNewUser({...newUser, is_admin: e.target.checked})}
                    className="mr-2"
                  />
                  <label className="text-sm">Administrator</label>
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

export default AdminPanel;