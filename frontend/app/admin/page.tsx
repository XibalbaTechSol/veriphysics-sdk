"use client";
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';
import { Shield, Users, Activity, CheckCircle, XCircle, Clock, Search } from 'lucide-react';

interface AdminStats {
    total_jobs: number;
    verified_jobs: number;
    failed_jobs: number;
    processing_jobs: number;
    users_count: number;
}

interface Job {
    id: number;
    status: string;
    score: number | null;
    verified: boolean | null;
    created_at: string;
    filename: string;
    user_id: number;
    message: string | null;
}

export default function AdminDashboard() {
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsRes, jobsRes] = await Promise.all([
                api.get('/admin/stats'),
                api.get('/admin/jobs')
            ]);
            setStats(statsRes.data);
            setJobs(jobsRes.data);
        } catch (err) {
            console.error("Admin access denied or error", err);
            router.push('/dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-white bg-gray-900 min-h-screen">Loading Admin Panel...</div>;

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                <header className="flex justify-between items-center mb-10 border-b border-gray-700 pb-4">
                    <div className="flex items-center space-x-3">
                        <Shield className="w-8 h-8 text-red-500" />
                        <h1 className="text-3xl font-bold tracking-tight">VeriPhysics <span className="text-red-500">Admin</span></h1>
                    </div>
                    <button onClick={() => router.push('/dashboard')} className="text-gray-400 hover:text-white">
                        Back to User Dashboard
                    </button>
                </header>

                {/* Stats Grid */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-gray-400 text-sm">Total Jobs</p>
                                    <h3 className="text-3xl font-bold mt-2">{stats.total_jobs}</h3>
                                </div>
                                <Activity className="text-blue-500" />
                            </div>
                        </div>
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-gray-400 text-sm">Verified Real</p>
                                    <h3 className="text-3xl font-bold mt-2 text-green-400">{stats.verified_jobs}</h3>
                                </div>
                                <CheckCircle className="text-green-500" />
                            </div>
                        </div>
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-gray-400 text-sm">Fakes Detected</p>
                                    <h3 className="text-3xl font-bold mt-2 text-red-400">{stats.failed_jobs}</h3>
                                </div>
                                <XCircle className="text-red-500" />
                            </div>
                        </div>
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-gray-400 text-sm">Total Users</p>
                                    <h3 className="text-3xl font-bold mt-2">{stats.users_count}</h3>
                                </div>
                                <Users className="text-purple-500" />
                            </div>
                        </div>
                    </div>
                )}

                {/* Global Jobs Table */}
                <section>
                    <h2 className="text-xl font-semibold mb-6 flex items-center">System-Wide Verification Log</h2>
                    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
                        <table className="w-full text-left">
                            <thead className="bg-gray-750 text-gray-400 text-xs uppercase bg-gray-900/50">
                                <tr>
                                    <th className="p-4">ID</th>
                                    <th className="p-4">User ID</th>
                                    <th className="p-4">File</th>
                                    <th className="p-4">Date</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Score</th>
                                    <th className="p-4">Verdict</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {jobs.map((j) => (
                                    <tr key={j.id} className="hover:bg-gray-750 transition-colors">
                                        <td className="p-4 font-mono text-gray-500">#{j.id}</td>
                                        <td className="p-4 text-blue-400">User #{j.user_id}</td>
                                        <td className="p-4 font-medium">{j.filename}</td>
                                        <td className="p-4 text-sm text-gray-400">{new Date(j.created_at).toLocaleString()}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${
                                                j.status === 'COMPLETED' ? 'bg-blue-900/50 text-blue-200' :
                                                j.status === 'FAILED' ? 'bg-red-900/50 text-red-200' :
                                                'bg-yellow-900/50 text-yellow-200'
                                            }`}>
                                                {j.status}
                                            </span>
                                        </td>
                                        <td className="p-4 font-mono">{j.score?.toFixed(4) || '-'}</td>
                                        <td className="p-4">
                                            {j.status === 'COMPLETED' ? (
                                                j.verified ?
                                                    <span className="flex items-center text-green-400 font-bold"><CheckCircle size={16} className="mr-2" /> REAL</span> :
                                                    <span className="flex items-center text-red-400 font-bold"><XCircle size={16} className="mr-2" /> FAKE</span>
                                            ) : '-'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </div>
    );
}
