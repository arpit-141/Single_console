import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await axios.get(`${API}/roles`);
      setRoles(response.data);
    } catch (error) {
      console.error('Error fetching roles:', error);
    }
  };

  const filteredUsers = users.filter(user => {
    if (searchTerm && !user.username.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !user.email.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    if (filter === 'all') return true;
    if (filter === 'admin') return user.is_admin;
    if (filter === 'active') return user.is_active;
    if (filter === 'inactive') return !user.is_active;
    return false;
  });

  const getRolesByAppType = () => {
    const rolesByApp = {};
    roles.forEach(role => {
      const appType = role.app_type || 'System';
      if (!rolesByApp[appType]) {
        rolesByApp[appType] = [];
      }
      rolesByApp[appType].push(role);
    });
    return rolesByApp;
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
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">User Management</h1>
          {isAdmin() && (
            <a
              href="/admin"
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
            >
              Manage Users
            </a>
          )}
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search users by username or email..."
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
                <option value="all">All Users</option>
                <option value="admin">Administrators</option>
                <option value="active">Active Users</option>
                <option value="inactive">Inactive Users</option>
              </select>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Users List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Users ({filteredUsers.length})</h2>
              
              {filteredUsers.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-4xl mb-4">👥</div>
                  <p className="text-gray-500">No users found matching your criteria.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredUsers.map((user) => (
                    <div key={user.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{user.username}</h3>
                            <span className={`px-2 py-1 rounded text-xs ${
                              user.is_admin 
                                ? 'bg-red-100 text-red-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {user.is_admin ? 'Admin' : 'User'}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${
                              user.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                          
                          <div className="text-gray-600 mb-2">
                            <div>{user.email}</div>
                            {(user.first_name || user.last_name) && (
                              <div className="text-sm">{user.first_name} {user.last_name}</div>
                            )}
                          </div>

                          <div className="mb-2">
                            <div className="text-sm text-gray-500 mb-1">Module Access:</div>
                            <div className="flex flex-wrap gap-1">
                              {user.module_access.length === 0 ? (
                                <span className="text-gray-400 text-sm">No module access</span>
                              ) : (
                                user.module_access.map((module) => (
                                  <span key={module} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                    {module}
                                  </span>
                                ))
                              )}
                            </div>
                          </div>

                          <div>
                            <div className="text-sm text-gray-500 mb-1">Roles:</div>
                            <div className="flex flex-wrap gap-1">
                              {user.roles.length === 0 ? (
                                <span className="text-gray-400 text-sm">No roles assigned</span>
                              ) : (
                                user.roles.map((role) => (
                                  <span key={role} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                                    {role}
                                  </span>
                                ))
                              )}
                            </div>
                          </div>

                          <div className="text-xs text-gray-400 mt-2">
                            Created: {new Date(user.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Roles Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">Available Roles ({roles.length})</h3>
              
              {Object.entries(getRolesByAppType()).map(([appType, appRoles]) => (
                <div key={appType} className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">{appType} Roles</h4>
                  <div className="space-y-2">
                    {appRoles.map((role) => (
                      <div key={role.id} className="border rounded p-3">
                        <div className="flex items-center justify-between mb-1">
                          <h5 className="font-medium text-sm">{role.name}</h5>
                          {role.is_synced && (
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                              Synced
                            </span>
                          )}
                        </div>
                        {role.description && (
                          <p className="text-xs text-gray-600 mb-1">{role.description}</p>
                        )}
                        <div className="text-xs text-gray-500">
                          Permissions: {role.permissions.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}

              {roles.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-4xl mb-4">🎭</div>
                  <p className="text-gray-500 text-sm">No roles configured yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;