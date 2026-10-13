"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { saathiApi } from "@/lib/api";
import type {
  SaathiDashboardStats,
  MechanicProfile,
  LearningModuleSummary,
  LearningModuleDetail,
  QuizResult,
  CustomerReferral,
  SaathiProgramInitiative,
} from "@/lib/types";
import {
  Award,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Clock,
  HelpCircle,
  Info,
  Layers,
  PlusCircle,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  UserCheck,
  Users,
  Wrench,
  X,
  AlertTriangle,
  Flame,
  FileCheck,
  TrendingUp,
} from "lucide-react";

type TabKey = "overview" | "learning" | "profile" | "referrals" | "eurogrip_concept";

export default function GripWiseSaathiPortal() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [stats, setStats] = useState<SaathiDashboardStats | null>(null);
  const [profile, setProfile] = useState<MechanicProfile | null>(null);
  const [modules, setModules] = useState<LearningModuleSummary[]>([]);
  const [referrals, setReferrals] = useState<CustomerReferral[]>([]);
  const [initiatives, setInitiatives] = useState<SaathiProgramInitiative[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  // Profile Edit Modal State
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({
    years_experience: 0,
    specialization: "",
    workshop_address: "",
    phone: "",
    bio: "",
  });
  const [savingProfile, setSavingProfile] = useState(false);

  // Learning Module / Quiz Modal State
  const [selectedModule, setSelectedModule] = useState<LearningModuleDetail | null>(null);
  const [loadingModule, setLoadingModule] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState<number[]>([]);
  const [quizSubmitting, setQuizSubmitting] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);

  // Referral Modal State
  const [showReferralModal, setShowReferralModal] = useState(false);
  const [referralForm, setReferralForm] = useState({
    customer_name_masked: "",
    customer_phone_masked: "",
    vehicle_model: "",
    tyre_need: "TREAD_WEAR_MONITORING",
    notes: "",
    consent_confirmed: true,
  });
  const [savingReferral, setSavingReferral] = useState(false);

  // Scoring Rules Modal
  const [showRulesModal, setShowRulesModal] = useState(false);

  const loadData = async () => {
    if (!user) return;
    try {
      setError("");
      const [dashData, profData, modsData, refsData, initsData] = await Promise.all([
        saathiApi.getDashboard(user.access_token),
        saathiApi.getProfile(user.access_token),
        saathiApi.getModules(user.access_token),
        saathiApi.getReferrals(user.access_token),
        saathiApi.getInitiatives(user.access_token),
      ]);
      setStats(dashData);
      setProfile(profData);
      setProfileForm({
        years_experience: profData.years_experience || 0,
        specialization: profData.specialization || "",
        workshop_address: profData.workshop_address || "",
        phone: profData.phone || "",
        bio: profData.bio || "",
      });
      setModules(modsData.modules);
      setReferrals(refsData.referrals);
      setInitiatives(initsData.initiatives);
    } catch (err: any) {
      setError(err.message || "Failed to load Saathi engagement data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    try {
      setSavingProfile(true);
      const updated = await saathiApi.updateProfile(user.access_token, {
        years_experience: Number(profileForm.years_experience),
        specialization: profileForm.specialization,
        workshop_address: profileForm.workshop_address,
        phone: profileForm.phone,
        bio: profileForm.bio,
      });
      setProfile(updated);
      setShowProfileModal(false);
      // Refresh stats to capture possible welcome badge award
      const refreshedStats = await saathiApi.getDashboard(user.access_token);
      setStats(refreshedStats);
    } catch (err: any) {
      alert("Failed to update profile: " + err.message);
    } finally {
      setSavingProfile(false);
    }
  };

  const handleOpenModule = async (moduleId: string) => {
    if (!user) return;
    try {
      setLoadingModule(true);
      setQuizResult(null);
      const detail = await saathiApi.getModuleDetail(user.access_token, moduleId);
      setSelectedModule(detail);
      setQuizAnswers(new Array(detail.quiz_questions.length).fill(-1));
    } catch (err: any) {
      alert("Failed to load module: " + err.message);
    } finally {
      setLoadingModule(false);
    }
  };

  const handleSelectQuizAnswer = (qIdx: number, optIdx: number) => {
    const updated = [...quizAnswers];
    updated[qIdx] = optIdx;
    setQuizAnswers(updated);
  };

  const handleSubmitQuiz = async () => {
    if (!user || !selectedModule) return;
    if (quizAnswers.some((a) => a === -1)) {
      alert("Please answer all questions before submitting.");
      return;
    }
    try {
      setQuizSubmitting(true);
      const res = await saathiApi.submitQuiz(user.access_token, selectedModule.id, quizAnswers);
      setQuizResult(res);
      // Reload modules list & dashboard stats
      const [modsRes, dashRes] = await Promise.all([
        saathiApi.getModules(user.access_token),
        saathiApi.getDashboard(user.access_token),
      ]);
      setModules(modsRes.modules);
      setStats(dashRes);
    } catch (err: any) {
      alert("Quiz submission failed: " + err.message);
    } finally {
      setQuizSubmitting(false);
    }
  };

  const handleCreateReferral = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    try {
      setSavingReferral(true);
      await saathiApi.createReferral(user.access_token, referralForm);
      setShowReferralModal(false);
      setReferralForm({
        customer_name_masked: "",
        customer_phone_masked: "",
        vehicle_model: "",
        tyre_need: "TREAD_WEAR_MONITORING",
        notes: "",
        consent_confirmed: true,
      });
      const [refRes, dashRes] = await Promise.all([
        saathiApi.getReferrals(user.access_token),
        saathiApi.getDashboard(user.access_token),
      ]);
      setReferrals(refRes.referrals);
      setStats(dashRes);
    } catch (err: any) {
      alert("Failed to create referral: " + err.message);
    } finally {
      setSavingReferral(false);
    }
  };

  const handleUpdateReferralStatus = async (
    referralId: string,
    newStatus: "CONTACTED" | "SERVICE_COMPLETED" | "EXPIRED"
  ) => {
    if (!user) return;
    try {
      await saathiApi.updateReferral(user.access_token, referralId, { status: newStatus });
      const [refRes, dashRes] = await Promise.all([
        saathiApi.getReferrals(user.access_token),
        saathiApi.getDashboard(user.access_token),
      ]);
      setReferrals(refRes.referrals);
      setStats(dashRes);
    } catch (err: any) {
      alert("Failed to update status: " + err.message);
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case "Master Saathi":
        return "text-purple-400 bg-purple-500/10 border-purple-500/30";
      case "Gold Saathi":
        return "text-amber-300 bg-amber-500/15 border-amber-500/30";
      case "Silver Saathi":
        return "text-slate-200 bg-slate-500/15 border-slate-400/30";
      default:
        return "text-orange-400 bg-orange-500/15 border-orange-500/30";
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Banner / Program Header */}
      <div className="rounded-2xl border border-orange-500/30 bg-gradient-to-br from-orange-500/10 via-[hsl(var(--color-surface-2))] to-amber-500/10 p-6 md:p-8 relative overflow-hidden">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-orange-500/20 text-orange-300 border border-orange-500/30 flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5" />
                Eurogrip TORQ Challenge 4.0 &bull; Case Study 4
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-300 border border-blue-500/20">
                Mechanic Advocacy &amp; Engagement Programme
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              GripWise Saathi <span className="text-orange-400 font-medium">Advocacy Hub</span>
            </h1>
            <p className="text-sm text-[hsl(var(--color-text-muted))] max-w-2xl leading-relaxed">
              Empowering two-wheeler workshop mechanics through certified tyre engineering knowledge, transparent
              participation recognition, physical diagnostic tracking, and trusted customer follow-ups.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => setShowRulesModal(true)}
              className="btn-secondary text-xs flex items-center gap-2 py-2"
            >
              <HelpCircle className="h-4 w-4 text-orange-400" />
              Scoring &amp; Ethics Rules
            </button>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="btn-secondary text-xs flex items-center gap-2 py-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
              Sync Data
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-[hsl(var(--color-border))] gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === "overview"
              ? "bg-[hsl(var(--color-surface-3))] text-white border border-[hsl(var(--color-border))] shadow-sm"
              : "text-[hsl(var(--color-text-muted))] hover:text-white"
          }`}
        >
          <Award className="h-4 w-4 text-orange-400" />
          Overview &amp; Badges
        </button>

        <button
          onClick={() => setActiveTab("learning")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === "learning"
              ? "bg-[hsl(var(--color-surface-3))] text-white border border-[hsl(var(--color-border))] shadow-sm"
              : "text-[hsl(var(--color-text-muted))] hover:text-white"
          }`}
        >
          <BookOpen className="h-4 w-4 text-blue-400" />
          Tyre-Care Learning Hub
          {stats && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-bold">
              {stats.completed_modules_count}/{stats.total_modules_count}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("profile")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === "profile"
              ? "bg-[hsl(var(--color-surface-3))] text-white border border-[hsl(var(--color-border))] shadow-sm"
              : "text-[hsl(var(--color-text-muted))] hover:text-white"
          }`}
        >
          <UserCheck className="h-4 w-4 text-emerald-400" />
          Workshop Profile
          {stats && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                stats.profile_completeness_percent >= 80
                  ? "bg-emerald-500/20 text-emerald-300"
                  : "bg-amber-500/20 text-amber-300"
              }`}
            >
              {stats.profile_completeness_percent}%
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("referrals")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === "referrals"
              ? "bg-[hsl(var(--color-surface-3))] text-white border border-[hsl(var(--color-border))] shadow-sm"
              : "text-[hsl(var(--color-text-muted))] hover:text-white"
          }`}
        >
          <Users className="h-4 w-4 text-amber-400" />
          Customer Follow-Ups
          {referrals.length > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-bold">
              {referrals.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("eurogrip_concept")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === "eurogrip_concept"
              ? "bg-[hsl(var(--color-surface-3))] text-white border border-[hsl(var(--color-border))] shadow-sm"
              : "text-[hsl(var(--color-text-muted))] hover:text-white"
          }`}
        >
          <Layers className="h-4 w-4 text-purple-400" />
          Eurogrip TORQ 4.0 Concept
        </button>
      </div>

      {loading ? (
        <div className="py-20 text-center text-[hsl(var(--color-text-muted))]">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-3 text-orange-400" />
          Loading GripWise Saathi Advocacy Data...
        </div>
      ) : (
        <>
          {/* TAB 1: OVERVIEW & BADGES */}
          {activeTab === "overview" && stats && (
            <div className="space-y-6">
              {/* Top Tier & Points Hero Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Tier Card */}
                <div className="card bg-gradient-to-b from-[hsl(var(--color-surface-2))] to-[hsl(var(--color-surface-3))] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs uppercase font-bold tracking-wider text-[hsl(var(--color-text-muted))]">
                        Participation Tier
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider ${getTierColor(
                          stats.tier
                        )}`}
                      >
                        {stats.tier}
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2 mb-1">
                      <span className="text-3xl font-extrabold text-white">{stats.total_points}</span>
                      <span className="text-xs text-[hsl(var(--color-text-muted))]">Engagement Points</span>
                    </div>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] mt-1">
                      {stats.next_tier
                        ? `${stats.points_to_next_tier} points to unlock ${stats.next_tier}`
                        : "Maximum Master Tier Achieved!"}
                    </p>
                  </div>

                  {/* Progress to next tier */}
                  <div className="mt-4 pt-4 border-t border-[hsl(var(--color-border))]">
                    <div className="w-full bg-[hsl(var(--color-surface))] rounded-full h-2 overflow-hidden border border-[hsl(var(--color-border))]">
                      <div
                        className="bg-orange-500 h-2 rounded-full transition-all duration-500"
                        style={{
                          width: `${
                            stats.tier === "Master Saathi"
                              ? 100
                              : Math.min(100, Math.max(5, (stats.total_points % 250) / 2.5))
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Profile Completeness Card */}
                <div className="card flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs uppercase font-bold tracking-wider text-[hsl(var(--color-text-muted))]">
                        Workshop Verification
                      </span>
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                          stats.profile_completeness_percent >= 80
                            ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                            : "bg-amber-500/15 text-amber-300 border-amber-500/30"
                        }`}
                      >
                        {stats.profile_completeness_percent}% Complete
                      </span>
                    </div>
                    <h3 className="font-bold text-lg text-white mb-1">{stats.workshop_name || stats.display_name}</h3>
                    <p className="text-xs text-[hsl(var(--color-text-muted))]">
                      {stats.workshop_city ? `Operating in ${stats.workshop_city}` : "Location not set"}
                    </p>
                  </div>

                  <div className="mt-4 pt-4 border-t border-[hsl(var(--color-border))] flex items-center justify-between">
                    <span className="text-xs text-[hsl(var(--color-text-muted))]">
                      {stats.profile_completeness_percent >= 80 ? "Verified Workshop" : "Incomplete profile"}
                    </span>
                    <button
                      onClick={() => setActiveTab("profile")}
                      className="text-xs font-semibold text-orange-400 hover:text-orange-300 flex items-center gap-1"
                    >
                      Complete Profile &rarr;
                    </button>
                  </div>
                </div>

                {/* Verifiable Activity Metrics */}
                <div className="card flex flex-col justify-between">
                  <div>
                    <span className="text-xs uppercase font-bold tracking-wider text-[hsl(var(--color-text-muted))] block mb-3">
                      Verifiable Actions Logged
                    </span>
                    <div className="grid grid-cols-2 gap-3 text-center">
                      <div className="p-2.5 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <div className="text-xl font-bold text-white">{stats.completed_modules_count}</div>
                        <div className="text-[11px] text-[hsl(var(--color-text-muted))]">Modules Passed</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <div className="text-xl font-bold text-white">{stats.verified_findings_count}</div>
                        <div className="text-[11px] text-[hsl(var(--color-text-muted))]">Findings Logged</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <div className="text-xl font-bold text-white">{stats.recorded_services_count}</div>
                        <div className="text-[11px] text-[hsl(var(--color-text-muted))]">Service Records</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <div className="text-xl font-bold text-white">{stats.completed_referrals_count}</div>
                        <div className="text-[11px] text-[hsl(var(--color-text-muted))]">Follow-Ups Done</div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 text-[11px] text-[hsl(var(--color-text-muted))] text-center">
                    All activities backed by real database records &amp; audit trails.
                  </div>
                </div>
              </div>

              {/* Earned Badges Showcase */}
              <div className="card space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                      <Award className="h-5 w-5 text-orange-400" />
                      Participation Badges &amp; Recognition
                    </h2>
                    <p className="text-xs text-[hsl(var(--color-text-muted))]">
                      Earned through real technical training, inspection diligence, and ethical recommendations.
                    </p>
                  </div>
                  <span className="text-xs font-semibold px-3 py-1 rounded-full bg-orange-500/10 text-orange-300 border border-orange-500/20">
                    {stats.badges_earned_count} of {stats.total_badges_count} Earned
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                  {stats.all_badges.map((badge) => (
                    <div
                      key={badge.id}
                      className={`p-4 rounded-xl border transition-all ${
                        badge.earned
                          ? "bg-[hsl(var(--color-surface-3))] border-orange-500/40 shadow-sm"
                          : "bg-[hsl(var(--color-surface-2))]/50 border-[hsl(var(--color-border))] opacity-60"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border ${
                            badge.earned
                              ? "bg-orange-500/20 text-orange-400 border-orange-500/40"
                              : "bg-[hsl(var(--color-surface-3))] text-[hsl(var(--color-text-muted))] border-[hsl(var(--color-border))]"
                          }`}
                        >
                          {badge.earned ? <CheckCircle2 className="h-5 w-5" /> : <Shield className="h-5 w-5" />}
                        </div>
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className="font-bold text-sm text-white">{badge.title}</h4>
                            {badge.earned ? (
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-500/20 text-green-300 font-semibold uppercase">
                                Unlocked
                              </span>
                            ) : (
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-500/20 text-slate-400 font-medium">
                                Locked
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-[hsl(var(--color-text-muted))]">{badge.description}</p>
                          <div className="text-[11px] text-orange-400/80 pt-1">
                            <span className="font-medium text-[hsl(var(--color-text-muted))]">Criteria: </span>
                            {badge.criteria_description}
                          </div>
                          {badge.earned && badge.earned_at && (
                            <div className="text-[10px] text-[hsl(var(--color-text-muted))] pt-1">
                              Awarded: {new Date(badge.earned_at).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Action Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div
                  onClick={() => setActiveTab("learning")}
                  className="card hover:border-blue-500/50 cursor-pointer transition-all flex items-center justify-between group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center group-hover:scale-105 transition-transform">
                      <BookOpen className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-base">Tyre-Care Learning Hub</h4>
                      <p className="text-xs text-[hsl(var(--color-text-muted))]">
                        Study wear patterns, inflation dynamics, and take quizzes (+50 pts each).
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-[hsl(var(--color-text-muted))] group-hover:text-white group-hover:translate-x-1 transition-all" />
                </div>

                <div
                  onClick={() => setActiveTab("referrals")}
                  className="card hover:border-amber-500/50 cursor-pointer transition-all flex items-center justify-between group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center group-hover:scale-105 transition-transform">
                      <Users className="h-6 w-6 text-amber-400" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-base">Customer Safety Follow-Ups</h4>
                      <p className="text-xs text-[hsl(var(--color-text-muted))]">
                        Track consented rider follow-ups &amp; maintain long-term customer relationships.
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-[hsl(var(--color-text-muted))] group-hover:text-white group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: TYRE-CARE LEARNING HUB */}
          {activeTab === "learning" && (
            <div className="space-y-6">
              {/* Educational Disclaimer Banner */}
              <div className="p-4 rounded-xl border border-blue-500/30 bg-blue-500/5 text-blue-300 text-xs flex items-start gap-3">
                <Info className="h-5 w-5 shrink-0 mt-0.5 text-blue-400" />
                <div>
                  <strong className="block text-sm text-blue-200 mb-0.5">
                    Technical Guidance &amp; Integrity Notice
                  </strong>
                  Educational modules provide general tyre engineering guidance based on ISO 4223, ETRTO, and
                  established two-wheeler maintenance practices. They do not constitute official Eurogrip
                  certifications, warranties, or endorsements. Points and badges reflect educational quiz completion.
                </div>
              </div>

              {/* Modules List Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {modules.map((m) => (
                  <div
                    key={m.id}
                    className="card flex flex-col justify-between hover:border-blue-500/50 transition-all group"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[hsl(var(--color-surface-3))] text-blue-400 font-bold border border-[hsl(var(--color-border))]">
                          {m.module_code}
                        </span>
                        {m.completed ? (
                          <span className="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full bg-green-500/20 text-green-300 font-semibold border border-green-500/30">
                            <CheckCircle2 className="h-3 w-3" /> Completed ({m.score_percent}%)
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full bg-slate-500/20 text-slate-300 font-medium">
                            <Clock className="h-3 w-3" /> ~{m.estimated_minutes} mins
                          </span>
                        )}
                      </div>

                      <h3 className="font-bold text-base text-white group-hover:text-blue-300 transition-colors">
                        {m.title}
                      </h3>

                      <p className="text-xs text-[hsl(var(--color-text-muted))] line-clamp-3 leading-relaxed">
                        {m.summary}
                      </p>

                      <div className="pt-2 text-[11px] text-[hsl(var(--color-text-muted))] flex items-center justify-between border-t border-[hsl(var(--color-border))]">
                        <span>Category: {m.category}</span>
                        <span className="font-semibold text-orange-400">+{m.points_reward} Points</span>
                      </div>
                    </div>

                    <div className="mt-5 pt-3">
                      <button
                        onClick={() => handleOpenModule(m.id)}
                        className={`w-full py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                          m.completed
                            ? "btn-secondary text-[hsl(var(--color-text))]"
                            : "bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20"
                        }`}
                      >
                        {m.completed ? "Review Module & Quiz" : "Start Module & Quiz &rarr;"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: WORKSHOP PROFILE */}
          {activeTab === "profile" && profile && (
            <div className="space-y-6">
              <div className="card">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[hsl(var(--color-border))]">
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      <UserCheck className="h-5 w-5 text-emerald-400" />
                      Mechanic Professional Profile
                    </h2>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] mt-1">
                      Real workshop information stored in GripWise database. Higher completeness unlocks the Verified
                      Workshop badge.
                    </p>
                  </div>
                  <button
                    onClick={() => setShowProfileModal(true)}
                    className="btn-primary text-xs flex items-center gap-2 py-2"
                  >
                    <Wrench className="h-3.5 w-3.5" />
                    Edit Profile Details
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
                  {/* Left Column: Completeness Meter */}
                  <div className="p-5 rounded-2xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))] space-y-4">
                    <span className="text-xs uppercase font-bold tracking-wider text-[hsl(var(--color-text-muted))]">
                      Profile Completion
                    </span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-extrabold text-white">{profile.completion_percent}%</span>
                      <span className="text-xs text-[hsl(var(--color-text-muted))]">Complete</span>
                    </div>

                    <div className="w-full bg-[hsl(var(--color-surface))] rounded-full h-2.5 overflow-hidden border border-[hsl(var(--color-border))]">
                      <div
                        className={`h-2.5 rounded-full transition-all duration-500 ${
                          profile.completion_percent >= 80 ? "bg-emerald-500" : "bg-amber-500"
                        }`}
                        style={{ width: `${profile.completion_percent}%` }}
                      />
                    </div>

                    <div className="space-y-2 pt-2 border-t border-[hsl(var(--color-border))]">
                      <span className="text-[11px] font-semibold text-[hsl(var(--color-text-muted))] uppercase">
                        Checklist:
                      </span>
                      {Object.entries(profile.completion_checklist).map(([k, done]) => (
                        <div key={k} className="flex items-center justify-between text-xs">
                          <span className="capitalize text-[hsl(var(--color-text-muted))]">
                            {k.replace(/_/g, " ")}
                          </span>
                          {done ? (
                            <span className="text-emerald-400 flex items-center gap-1 font-semibold text-[11px]">
                              <CheckCircle2 className="h-3 w-3" /> Done
                            </span>
                          ) : (
                            <span className="text-amber-400 text-[11px]">Missing</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Right Column: Displayed Profile Data */}
                  <div className="md:col-span-2 space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <span className="label">Mechanic Name</span>
                        <div className="font-semibold text-white text-sm">{profile.display_name}</div>
                      </div>

                      <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <span className="label">Workshop Name</span>
                        <div className="font-semibold text-white text-sm">{profile.workshop_name || "Not set"}</div>
                      </div>

                      <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <span className="label">City / Region</span>
                        <div className="font-semibold text-white text-sm">{profile.workshop_city || "Not set"}</div>
                      </div>

                      <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <span className="label">Years of Experience</span>
                        <div className="font-semibold text-white text-sm">
                          {profile.years_experience ? `${profile.years_experience} Years` : "Not specified"}
                        </div>
                      </div>

                      <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <span className="label">Specialization</span>
                        <div className="font-semibold text-white text-sm">
                          {profile.specialization || "General Two-Wheeler Mechanic"}
                        </div>
                      </div>

                      <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                        <span className="label">Contact Phone</span>
                        <div className="font-semibold text-white text-sm">{profile.phone || "Not set"}</div>
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                      <span className="label">Workshop Address</span>
                      <div className="text-sm text-white">{profile.workshop_address || "No address provided"}</div>
                    </div>

                    <div className="p-4 rounded-xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                      <span className="label">Professional Bio &amp; Background</span>
                      <p className="text-sm text-[hsl(var(--color-text-muted))] leading-relaxed">
                        {profile.bio || "No biography added yet. Click Edit Profile to tell riders about your experience."}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: CUSTOMER FOLLOW-UPS & REFERRALS */}
          {activeTab === "referrals" && (
            <div className="space-y-6">
              <div className="card">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[hsl(var(--color-border))]">
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      <Users className="h-5 w-5 text-amber-400" />
                      Consent-Aware Customer Follow-Ups
                    </h2>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] mt-1">
                      Track upcoming tyre checkups, seasonal monsoon checks, and replacement reminders. Customer data is
                      masked for privacy.
                    </p>
                  </div>
                  <button
                    onClick={() => setShowReferralModal(true)}
                    className="btn-primary text-xs flex items-center gap-2 py-2 bg-amber-600 hover:bg-amber-500"
                  >
                    <PlusCircle className="h-4 w-4" />
                    Log New Follow-Up
                  </button>
                </div>

                {/* Privacy & Ethical Guarantee */}
                <div className="my-4 p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-amber-300 text-xs flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 shrink-0 text-amber-400" />
                  <span>
                    <strong>Privacy Standard:</strong> Minimal customer references stored. No unsolicited commercial
                    marketing or third-party data sharing. Follow-ups must be pre-consented by the customer.
                  </span>
                </div>

                {referrals.length === 0 ? (
                  <div className="py-14 text-center border-2 border-dashed border-[hsl(var(--color-border))] rounded-2xl">
                    <Users className="h-10 w-10 text-[hsl(var(--color-text-muted))] mx-auto mb-3 opacity-40" />
                    <h3 className="font-bold text-base text-white mb-1">No Customer Follow-Ups Logged Yet</h3>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] max-w-sm mx-auto mb-4">
                      When servicing a customer vehicle, offer to log a follow-up inspection reminder (e.g., in 3,000 km
                      or before the rainy season).
                    </p>
                    <button
                      onClick={() => setShowReferralModal(true)}
                      className="btn-secondary text-xs inline-flex items-center gap-2"
                    >
                      <PlusCircle className="h-3.5 w-3.5" /> Log First Follow-Up
                    </button>
                  </div>
                ) : (
                  <div className="grid gap-3 pt-2">
                    {referrals.map((r) => (
                      <div
                        key={r.id}
                        className="p-4 rounded-xl border border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface-3))] flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-3">
                            <span className="font-bold text-sm text-white">{r.customer_name_masked}</span>
                            <span className="text-xs text-[hsl(var(--color-text-muted))] font-mono">
                              ({r.customer_phone_masked || "No Phone"})
                            </span>
                            <span
                              className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                                r.status === "SERVICE_COMPLETED"
                                  ? "bg-green-500/20 text-green-300 border border-green-500/30"
                                  : r.status === "CONTACTED"
                                  ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                                  : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                              }`}
                            >
                              {r.status.replace(/_/g, " ")}
                            </span>
                          </div>

                          <div className="text-xs text-[hsl(var(--color-text-muted))] flex flex-wrap gap-4 pt-0.5">
                            <span>Vehicle: <strong className="text-white">{r.vehicle_model}</strong></span>
                            <span>Need: <strong className="text-orange-400 capitalize">{r.tyre_need.replace(/_/g, " ").toLowerCase()}</strong></span>
                            <span>Created: {new Date(r.created_at).toLocaleDateString()}</span>
                          </div>

                          {r.notes && (
                            <p className="text-xs text-[hsl(var(--color-text-muted))] italic pt-1">
                              &ldquo;{r.notes}&rdquo;
                            </p>
                          )}
                        </div>

                        {/* Status update buttons */}
                        <div className="flex items-center gap-2 shrink-0">
                          {r.status === "PENDING" && (
                            <button
                              onClick={() => handleUpdateReferralStatus(r.id, "CONTACTED")}
                              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600/30 text-blue-300 hover:bg-blue-600/50 border border-blue-500/40"
                            >
                              Mark Contacted
                            </button>
                          )}

                          {r.status !== "SERVICE_COMPLETED" && (
                            <button
                              onClick={() => handleUpdateReferralStatus(r.id, "SERVICE_COMPLETED")}
                              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-green-600/30 text-green-300 hover:bg-green-600/50 border border-green-500/40"
                            >
                              Mark Service Done (+20 pts)
                            </button>
                          )}

                          {r.status === "SERVICE_COMPLETED" && (
                            <span className="text-xs text-green-400 flex items-center gap-1 font-medium">
                              <CheckCircle2 className="h-3.5 w-3.5" /> Completed
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 5: EUROGRIP TORQ CHALLENGE 4.0 CASE STUDY 4 CONCEPT */}
          {activeTab === "eurogrip_concept" && (
            <div className="space-y-6">
              <div className="card space-y-6">
                <div>
                  <span className="text-xs font-bold text-orange-400 uppercase tracking-wider block mb-1">
                    Strategic Concept Formulation
                  </span>
                  <h2 className="text-2xl font-extrabold text-white">
                    Eurogrip TORQ Challenge 4.0 &bull; Case Study 4 Solution Architecture
                  </h2>
                  <p className="text-xs text-[hsl(var(--color-text-muted))] mt-1 max-w-3xl leading-relaxed">
                    How tyre brands can convert transactional, margin-discount mechanic relationships into
                    accredited technical advocacy, professional dignity, and sustainable two-wheeler rider trust.
                  </p>
                </div>

                {/* Explicit Disclaimer */}
                <div className="demo-banner">
                  <Info className="h-4 w-4 shrink-0" />
                  <span>
                    <strong>Academic &amp; Case Study Disclaimer:</strong> GripWise Saathi is a proposed strategic
                    programme designed for Eurogrip TORQ Challenge 4.0, Case Study 4. This prototype does not claim an
                    official corporate partnership, funding, or existing contractual relationship with Eurogrip.
                  </span>
                </div>

                {/* Core Pillar Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                  <div className="p-5 rounded-2xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))] space-y-2">
                    <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/30 flex items-center justify-center text-orange-400 font-bold mb-2">
                      1
                    </div>
                    <h4 className="font-bold text-white text-sm">Professional Empowerment</h4>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] leading-relaxed">
                      Move away from transactional scratch-card discounts. Provide mechanics with structured tyre
                      knowledge, diagnostics tools, and verified digital credentials that enhance their standing with
                      local riders.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))] space-y-2">
                    <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold mb-2">
                      2
                    </div>
                    <h4 className="font-bold text-white text-sm">Evidence-Based Advocacy</h4>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] leading-relaxed">
                      Equip workshops with precision depth gauges and digital inspection audits. When recommendations
                      are rooted in verifiable millimetre depth and PSI data, riders trust the advice and choose quality
                      tyres willingly.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))] space-y-2">
                    <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold mb-2">
                      3
                    </div>
                    <h4 className="font-bold text-white text-sm">Ethical Loyalty &amp; Retention</h4>
                    <p className="text-xs text-[hsl(var(--color-text-muted))] leading-relaxed">
                      Prevent brand bias fatigue. Mechanics recommend products matched to rider riding conditions (daily
                      commute vs monsoon grip) while retaining transparent audit trails on the rider&apos;s mobile phone.
                    </p>
                  </div>
                </div>

                {/* Proposed Tool Support & Brand Education Initiatives */}
                <div className="space-y-4 pt-4 border-t border-[hsl(var(--color-border))]">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-lg text-white">Proposed Programme Initiatives</h3>
                      <p className="text-xs text-[hsl(var(--color-text-muted))]">
                        Configurable initiatives that a tyre manufacturer can sponsor for accredited workshops.
                      </p>
                    </div>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-semibold border border-purple-500/30">
                      {initiatives.length} Proposed Concepts
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {initiatives.map((init) => (
                      <div
                        key={init.id}
                        className="p-4 rounded-xl border border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface-3))] space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider bg-orange-500/15 text-orange-300 border border-orange-500/20">
                            {init.category.replace(/_/g, " ")}
                          </span>
                          <span className="text-[11px] text-[hsl(var(--color-text-muted))]">
                            Eligible at: <strong className="text-white">{init.eligibility_level} Tier</strong>
                          </span>
                        </div>
                        <h4 className="font-bold text-sm text-white">{init.title}</h4>
                        <p className="text-xs text-[hsl(var(--color-text-muted))] leading-relaxed">
                          {init.description}
                        </p>
                        {init.tool_specs && (
                          <div className="pt-2 text-[11px] text-[hsl(var(--color-text-muted))] border-t border-[hsl(var(--color-border))]">
                            {Object.entries(init.tool_specs).map(([k, v]) => (
                              <div key={k} className="flex justify-between py-0.5">
                                <span className="capitalize">{k.replace(/_/g, " ")}:</span>
                                <span className="text-white font-medium">{v}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* MODAL 1: EDIT PROFILE */}
      {showProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="card max-w-lg w-full bg-[hsl(var(--color-surface-2))] border-[hsl(var(--color-border))] space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[hsl(var(--color-border))]">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Wrench className="h-5 w-5 text-orange-400" />
                Update Professional Profile
              </h3>
              <button
                onClick={() => setShowProfileModal(false)}
                className="text-[hsl(var(--color-text-muted))] hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div>
                <label className="label">Years of Experience</label>
                <input
                  type="number"
                  min="0"
                  max="60"
                  value={profileForm.years_experience}
                  onChange={(e) => setProfileForm({ ...profileForm, years_experience: Number(e.target.value) })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">Specialization</label>
                <input
                  type="text"
                  placeholder="e.g. Tubeless Tyre Diagnostics, Wheel Truing"
                  value={profileForm.specialization}
                  onChange={(e) => setProfileForm({ ...profileForm, specialization: e.target.value })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">Workshop Street Address</label>
                <textarea
                  rows={2}
                  placeholder="Shop number, street, landmark..."
                  value={profileForm.workshop_address}
                  onChange={(e) => setProfileForm({ ...profileForm, workshop_address: e.target.value })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">Contact Phone</label>
                <input
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={profileForm.phone}
                  onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Bio &amp; Workshop Background</label>
                <textarea
                  rows={3}
                  placeholder="Tell riders about your workshop experience and services..."
                  value={profileForm.bio}
                  onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                  className="input"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[hsl(var(--color-border))]">
                <button
                  type="button"
                  onClick={() => setShowProfileModal(false)}
                  className="btn-secondary text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingProfile}
                  className="btn-primary text-xs flex items-center gap-2"
                >
                  {savingProfile && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
                  Save Profile Details
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: LEARNING MODULE DETAIL & QUIZ */}
      {selectedModule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="card max-w-3xl w-full bg-[hsl(var(--color-surface-2))] border-[hsl(var(--color-border))] max-h-[90vh] overflow-y-auto space-y-6">
            <div className="flex items-start justify-between pb-4 border-b border-[hsl(var(--color-border))] sticky top-0 bg-[hsl(var(--color-surface-2))] z-10">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[hsl(var(--color-surface-3))] text-blue-400 font-bold">
                    {selectedModule.module_code}
                  </span>
                  <span className="text-xs text-[hsl(var(--color-text-muted))]">
                    ~{selectedModule.estimated_minutes} min read &bull; +{selectedModule.points_reward} Points
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white">{selectedModule.title}</h3>
              </div>
              <button
                onClick={() => setSelectedModule(null)}
                className="text-[hsl(var(--color-text-muted))] hover:text-white p-1"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Technical source reminder */}
            <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs flex items-center gap-2">
              <Info className="h-4 w-4 shrink-0" />
              <span>
                <strong>Verified Technical Basis:</strong> {selectedModule.technical_source} (General engineering
                standard).
              </span>
            </div>

            {/* Markdown Body preview */}
            <div className="prose prose-invert max-w-none text-xs text-[hsl(var(--color-text))] leading-relaxed space-y-3 bg-[hsl(var(--color-surface-3))] p-4 rounded-xl border border-[hsl(var(--color-border))]">
              <div className="whitespace-pre-line">{selectedModule.content_markdown}</div>
            </div>

            {/* QUIZ SECTION */}
            <div className="space-y-4 pt-4 border-t border-[hsl(var(--color-border))]">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-base text-white flex items-center gap-2">
                  <HelpCircle className="h-5 w-5 text-orange-400" />
                  Technical Knowledge Check (3 Questions)
                </h4>
                <span className="text-xs text-[hsl(var(--color-text-muted))]">Pass threshold: 66%+</span>
              </div>

              {quizResult && (
                <div
                  className={`p-4 rounded-xl border ${
                    quizResult.passed
                      ? "bg-green-500/15 border-green-500/30 text-green-200"
                      : "bg-red-500/15 border-red-500/30 text-red-200"
                  }`}
                >
                  <div className="flex items-center gap-2 font-bold text-sm mb-1">
                    {quizResult.passed ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
                    <span>{quizResult.passed ? "Congratulations! Module Passed!" : "Score Below 66%. Review Guidance & Retake."}</span>
                  </div>
                  <p className="text-xs">
                    Score: <strong>{quizResult.score_percent}%</strong> &bull; Points Awarded:{" "}
                    <strong>+{quizResult.points_awarded}</strong> &bull; Current Tier:{" "}
                    <strong>{quizResult.tier}</strong>
                  </p>
                  {quizResult.newly_earned_badges.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-green-500/30 text-xs text-green-300 flex items-center gap-1.5 font-semibold">
                      <Sparkles className="h-4 w-4" />
                      New Badges Unlocked: {quizResult.newly_earned_badges.join(", ")}
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-4">
                {selectedModule.quiz_questions.map((q, qIdx) => {
                  const feedback = quizResult?.feedback?.find((f) => f.question_id === q.id);
                  return (
                    <div
                      key={q.id}
                      className="p-4 rounded-xl border border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface-3))] space-y-3"
                    >
                      <div className="font-semibold text-xs text-white">
                        Q{qIdx + 1}: {q.prompt}
                      </div>

                      <div className="space-y-1.5">
                        {q.options.map((opt, optIdx) => {
                          const isSelected = quizAnswers[qIdx] === optIdx;
                          return (
                            <label
                              key={optIdx}
                              onClick={() => handleSelectQuizAnswer(qIdx, optIdx)}
                              className={`flex items-start gap-2.5 p-2.5 rounded-lg border text-xs cursor-pointer transition-all ${
                                isSelected
                                  ? "bg-blue-600/20 border-blue-500 text-white"
                                  : "bg-[hsl(var(--color-surface-2))] border-[hsl(var(--color-border))] text-[hsl(var(--color-text-muted))] hover:text-white"
                              }`}
                            >
                              <input
                                type="radio"
                                name={`q_${q.id}`}
                                checked={isSelected}
                                onChange={() => handleSelectQuizAnswer(qIdx, optIdx)}
                                className="mt-0.5"
                              />
                              <span>{opt}</span>
                            </label>
                          );
                        })}
                      </div>

                      {feedback && (
                        <div
                          className={`p-2.5 rounded-lg text-xs mt-2 ${
                            feedback.is_correct
                              ? "bg-green-500/10 text-green-300 border border-green-500/20"
                              : "bg-red-500/10 text-red-300 border border-red-500/20"
                          }`}
                        >
                          <strong>{feedback.is_correct ? "Correct!" : "Incorrect."}</strong> {feedback.explanation}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setSelectedModule(null)}
                  className="btn-secondary text-xs"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={handleSubmitQuiz}
                  disabled={quizSubmitting || quizAnswers.some((a) => a === -1)}
                  className="btn-primary text-xs flex items-center gap-2 bg-blue-600 hover:bg-blue-500"
                >
                  {quizSubmitting && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
                  Submit Answers &amp; Grade Quiz
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: LOG CUSTOMER FOLLOW-UP */}
      {showReferralModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="card max-w-lg w-full bg-[hsl(var(--color-surface-2))] border-[hsl(var(--color-border))] space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[hsl(var(--color-border))]">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Users className="h-5 w-5 text-amber-400" />
                Log Customer Safety Follow-Up
              </h3>
              <button
                onClick={() => setShowReferralModal(false)}
                className="text-[hsl(var(--color-text-muted))] hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateReferral} className="space-y-4">
              <div>
                <label className="label">Customer Reference (Masked / First Name Only)</label>
                <input
                  type="text"
                  placeholder="e.g. Ramesh K. (avoid full confidential names)"
                  value={referralForm.customer_name_masked}
                  onChange={(e) => setReferralForm({ ...referralForm, customer_name_masked: e.target.value })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">Customer Phone (Masked Reference)</label>
                <input
                  type="text"
                  placeholder="e.g. +91 98*** **321"
                  value={referralForm.customer_phone_masked}
                  onChange={(e) => setReferralForm({ ...referralForm, customer_phone_masked: e.target.value })}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Two-Wheeler Model</label>
                <input
                  type="text"
                  placeholder="e.g. Hero Splendor Plus, Bajaj Pulsar 150"
                  value={referralForm.vehicle_model}
                  onChange={(e) => setReferralForm({ ...referralForm, vehicle_model: e.target.value })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">Tyre Safety Purpose / Need</label>
                <select
                  value={referralForm.tyre_need}
                  onChange={(e) => setReferralForm({ ...referralForm, tyre_need: e.target.value })}
                  className="input"
                >
                  <option value="TREAD_WEAR_MONITORING">Tread Wear Monitoring (Approaching 2mm)</option>
                  <option value="REPLACEMENT_INSPECTION">Pre-Monsoon Replacement Check</option>
                  <option value="PRESSURE_CHECK">Periodic Pressure &amp; Valve Stem Check</option>
                  <option value="PUNCTURE_FOLLOWUP">Puncture Combi-Patch Follow-Up</option>
                </select>
              </div>

              <div>
                <label className="label">Technical Notes / Next Visit Target</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Rear tyre tread 2.2mm, rider will return before monsoon in July..."
                  value={referralForm.notes}
                  onChange={(e) => setReferralForm({ ...referralForm, notes: e.target.value })}
                  className="input"
                />
              </div>

              <div className="flex items-center gap-2 p-3 rounded-lg bg-[hsl(var(--color-surface-3))] border border-[hsl(var(--color-border))]">
                <input
                  type="checkbox"
                  id="consent"
                  checked={referralForm.consent_confirmed}
                  onChange={(e) => setReferralForm({ ...referralForm, consent_confirmed: e.target.checked })}
                  className="rounded"
                  required
                />
                <label htmlFor="consent" className="text-xs text-[hsl(var(--color-text-muted))] cursor-pointer">
                  Customer has consented to this tyre checkup reminder at this workshop.
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[hsl(var(--color-border))]">
                <button
                  type="button"
                  onClick={() => setShowReferralModal(false)}
                  className="btn-secondary text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingReferral}
                  className="btn-primary text-xs flex items-center gap-2 bg-amber-600 hover:bg-amber-500"
                >
                  {savingReferral && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
                  Save Follow-Up
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 4: SCORING & ETHICS RULES */}
      {showRulesModal && stats && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="card max-w-2xl w-full bg-[hsl(var(--color-surface-2))] border-[hsl(var(--color-border))] space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[hsl(var(--color-border))]">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-orange-400" />
                Transparent Scoring &amp; Ethical Safeguards
              </h3>
              <button
                onClick={() => setShowRulesModal(false)}
                className="text-[hsl(var(--color-text-muted))] hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-300 text-xs">
              <strong>Zero Brand-Bias Rule:</strong> GripWise Saathi points are awarded strictly for verifiable technical
              diligence, education, and genuine customer care. Mechanics are never rewarded for pushing any specific
              brand regardless of rider needs.
            </div>

            <div className="space-y-3">
              {stats.scoring_rules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-[hsl(var(--color-border))] bg-[hsl(var(--color-surface-3))] space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-xs">{rule.activity}</span>
                    <span className="font-extrabold text-orange-400 text-xs">+{rule.points} Points</span>
                  </div>
                  <p className="text-xs text-[hsl(var(--color-text-muted))]">{rule.description}</p>
                  <div className="text-[11px] text-emerald-400 pt-1">
                    <span className="font-semibold text-[hsl(var(--color-text-muted))]">Safeguard: </span>
                    {rule.ethical_safeguard}
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-[hsl(var(--color-border))] flex justify-end">
              <button onClick={() => setShowRulesModal(false)} className="btn-secondary text-xs">
                Understood
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
