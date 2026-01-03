"use client";
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';
import { Key, Shield, AlertTriangle, CheckCircle, XCircle, Plus, LogOut } from 'lucide-react';

interface ApiKey {
    key: string;
    active: boolean;
    created: string;
}

interface Job {
    id: number;
    status: string;
    score: number | null;
    verified: boolean | null;
    created_at: string;
    filename: string;
}

export default function DashboardPage() {
    const [keys, setKeys] = useState<ApiKey[]>([]);
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);
    const router = useRouter();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [keysRes, jobsRes, userRes] = await Promise.all([
                api.get('/api-keys'),
                api.get('/jobs'),
                api.get('/users/me')
            ]);
            setKeys(keysRes.data);
            setJobs(jobsRes.data);
            setIsAdmin(userRes.data.is_admin);
        } catch (err) {
            router.push('/login');
        } finally {
            setLoading(false);
        }
    };

    const createKey = async () => {
        try {
            await api.post('/api-keys');
            fetchData();
        } catch (err) {
            alert("Failed to create key");
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        router.push('/login');
    };

    if (loading) return <div className="p-8 text-white bg-gray-900 min-h-screen">Loading...</div>;

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <header className="flex justify-between items-center mb-10 border-b border-gray-700 pb-4">
                    <div className="flex items-center space-x-3">
                        <Shield className="w-8 h-8 text-blue-500" />
                        <h1 className="text-3xl font-bold tracking-tight">VeriPhysics <span className="text-sm font-normal text-gray-400">Dashboard</span></h1>
                    </div>
                    <div className="flex items-center space-x-6">
                        {isAdmin && (
                            <button 
                                onClick={() => router.push('/admin')}
                                className="px-4 py-2 bg-red-900/50 text-red-200 border border-red-800 rounded hover:bg-red-900 transition-colors flex items-center"
                            >
                                <Shield size={16} className="mr-2" />
                                Admin Panel
                            </button>
                        )}
                        <button onClick={logout} className="flex items-center space-x-2 text-gray-400 hover:text-white">
                            <LogOut size={16} /> <span>Sign Out</span>
                        </button>
                    </div>
                </header>

                {/* API Keys Section */}
                <section className="mb-12">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold flex items-center"><Key className="mr-2" /> API Keys</h2>
                        <button onClick={createKey} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center text-sm font-medium transition">
                            <Plus size={16} className="mr-1" /> Create Key
                        </button>
                    </div>
                    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
                        <table className="w-full text-left">
                            <thead className="bg-gray-750 text-gray-400 text-xs uppercase">
                                <tr>
                                    <th className="p-4">Key</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Created</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {keys.map((k) => (
                                    <tr key={k.key} className="hover:bg-gray-750">
                                        <td className="p-4 font-mono text-blue-400">{k.key}</td>
                                        <td className="p-4"><span className="bg-green-900 text-green-300 text-xs px-2 py-1 rounded">Active</span></td>
                                        <td className="p-4 text-gray-400 text-sm">{new Date(k.created).toLocaleDateString()}</td>
                                    </tr>
                                ))}
                                {keys.length === 0 && <tr><td colSpan={3} className="p-8 text-center text-gray-500">No API Keys found. Create one to get started.</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </section>

                {/* Jobs Section */}
                <section>
                    <h2 className="text-xl font-semibold mb-6 flex items-center"><Shield className="mr-2" /> Verification Jobs</h2>
                    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
                        <table className="w-full text-left">
                            <thead className="bg-gray-750 text-gray-400 text-xs uppercase">
                                <tr>
                                    <th className="p-4">Job ID</th>
                                    <th className="p-4">File</th>
                                    <th className="p-4">Date</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Score</th>
                                    <th className="p-4">Result</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {jobs.map((j) => (
                                    <tr key={j.id} className="hover:bg-gray-750">
                                        <td className="p-4 text-gray-400">#{j.id}</td>
                                        <td className="p-4">{j.filename}</td>
                                        <td className="p-4 text-sm text-gray-400">{new Date(j.created_at).toLocaleString()}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${j.status === 'COMPLETED' ? 'bg-blue-900 text-blue-200' :
                                                    j.status === 'FAILED' ? 'bg-red-900 text-red-200' :
                                                        'bg-yellow-900 text-yellow-200'
                                                }`}>
                                                {j.status}
                                            </span>
                                        </td>
                                        <td className="p-4 font-mono">{j.score?.toFixed(4) || '-'}</td>
                                        <td className="p-4">
                                            {j.status === 'COMPLETED' ? (
                                                j.verified ?
                                                    <span className="flex items-center text-green-400"><CheckCircle size={16} className="mr-1" /> REAL</span> :
                                                    <span className="flex items-center text-red-400"><AlertTriangle size={16} className="mr-1" /> FAKE</span>
                                            ) : '-'}
                                        </td>
                                    </tr>
                                ))}
                                {jobs.length === 0 && <tr><td colSpan={6} className="p-8 text-center text-gray-500">No verification jobs yet.</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </div>
    );
}
