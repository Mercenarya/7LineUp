from django.shortcuts import render, redirect
from django.contrib import messages
from sqlalchemy.orm import joinedload
from .database import Session, Member, Team, Match
from datetime import datetime

def get_session():
    return Session()

def index(request):
    session = get_session()
    members_count = session.query(Member).count()
    teams_count = session.query(Team).count()
    matches_count = session.query(Match).count()
    wins = session.query(Match).filter(Match.win == True).count()
    losses = session.query(Match).filter(Match.win == False).count()
    win_rate = 0
    if wins + losses > 0:
        win_rate = round((wins / (wins + losses)) * 100)
    session.close()
    context = {
        'members_count': members_count,
        'teams_count': teams_count,
        'matches_count': matches_count,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate
    }
    return render(request, 'core/index.html', context)

# Member views
def member_list(request):
    session = get_session()
    members = session.query(Member).all()
    session.close()
    return render(request, 'core/member_list.html', {'members': members})

def member_add(request):
    if request.method == 'POST':
        session = get_session()
        name = request.POST.get('name')
        ingame = request.POST.get('ingame')
        role = request.POST.get('role')
        notes = request.POST.get('notes')
        member = Member(name=name, ingame=ingame, role=role, notes=notes)
        session.add(member)
        session.commit()
        session.close()
        messages.success(request, 'Member added successfully.')
        return redirect('member_list')
    return render(request, 'core/member_form.html')

def member_edit(request, member_id):
    session = get_session()
    member = session.query(Member).get(member_id)
    if not member:
        session.close()
        messages.error(request, 'Member not found.')
        return redirect('member_list')
    if request.method == 'POST':
        member.name = request.POST.get('name')
        member.ingame = request.POST.get('ingame')
        member.role = request.POST.get('role')
        member.notes = request.POST.get('notes')
        session.commit()
        session.close()
        messages.success(request, 'Member updated successfully.')
        return redirect('member_list')
    session.close()
    return render(request, 'core/member_form.html', {'member': member})

def member_delete(request, member_id):
    session = get_session()
    member = session.query(Member).get(member_id)
    if member:
        session.delete(member)
        session.commit()
        session.close()
        messages.success(request, 'Member deleted successfully.')
    else:
        session.close()
        messages.error(request, 'Member not found.')
    return redirect('member_list')

# Team views
def team_list(request):
    session = get_session()
    teams = session.query(Team).options(joinedload(Team.members)).all()
    session.close()
    return render(request, 'core/team_list.html', {'teams': teams})

def team_add(request):
    session = get_session()
    if request.method == 'POST':
        name = request.POST.get('name')
        rank = request.POST.get('rank')
        role = request.POST.get('role')
        member_ids = request.POST.getlist('members')

        team = Team(name=name, rank=rank, role=role)
        if member_ids:
            members = session.query(Member).filter(Member.id.in_(member_ids)).all()
            team.members = members

        session.add(team)
        session.commit()
        session.close()
        messages.success(request, 'Team added successfully.')
        return redirect('team_list')

    # GET: cần danh sách members để hiển thị checkbox
    all_members = session.query(Member).all()
    session.close()
    return render(request, 'core/team_form.html', {'all_members': all_members})

def team_edit(request, team_id):
    session = get_session()
    team = session.query(Team).options(joinedload(Team.members)).get(team_id)
    if not team:
        session.close()
        messages.error(request, 'Team not found.')
        return redirect('team_list')

    if request.method == 'POST':
        team.name = request.POST.get('name')
        team.rank = request.POST.get('rank')
        team.role = request.POST.get('role')
        member_ids = request.POST.getlist('members')
        members = session.query(Member).filter(Member.id.in_(member_ids)).all() if member_ids else []
        team.members = members

        session.commit()
        session.close()
        messages.success(request, 'Team updated successfully.')
        return redirect('team_list')

    # GET: cần cả toàn bộ member (để hiện checkbox) và id các member đã thuộc team (để tick sẵn)
    all_members = session.query(Member).all()
    selected_ids = [m.id for m in team.members]
    session.close()
    return render(request, 'core/team_form.html', {
        'team': team,
        'all_members': all_members,
        'selected_ids': selected_ids
    })

def team_delete(request, team_id):
    session = get_session()
    team = session.query(Team).get(team_id)
    if team:
        session.delete(team)
        session.commit()
        session.close()
        messages.success(request, 'Team deleted successfully.')
    else:
        session.close()
        messages.error(request, 'Team not found.')
    return redirect('team_list')

# Match views
def match_list(request):
    session = get_session()
    matches = session.query(Match).options(joinedload(Match.team)).all()
    session.close()
    return render(request, 'core/match_list.html', {'matches': matches})

def match_add(request):
    if request.method == 'POST':
        session = get_session()
        opponent = request.POST.get('opponent')
        match_date_str = request.POST.get('match_date')
        rules = request.POST.get('rules')
        win_str = request.POST.get('win')
        if win_str == 'win':
            win = True
        elif win_str == 'loss':
            win = False
        else:
            win = None  # draw
        notes = request.POST.get('notes')
        team_id = request.POST.get('team')
        try:
            match_date = datetime.strptime(match_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            session.close()
            messages.error(request, 'Invalid date format.')
            return redirect('match_add')
        match = Match(
            opponent=opponent,
            match_date=match_date,
            rules=rules,
            win=win,
            notes=notes,
            team_id=team_id
        )
        session.add(match)
        session.commit()
        session.close()
        messages.success(request, 'Match added successfully.')
        return redirect('match_list')
    # GET request: show form with teams
    session = get_session()
    teams = session.query(Team).all()
    session.close()
    return render(request, 'core/match_form.html', {'teams': teams})

def match_edit(request, match_id):
    session = get_session()
    match = session.query(Match).get(match_id)
    if not match:
        session.close()
        messages.error(request, 'Match not found.')
        return redirect('match_list')
    if request.method == 'POST':
        match.opponent = request.POST.get('opponent')
        match_date_str = request.POST.get('match_date')
        rules = request.POST.get('rules')
        win_str = request.POST.get('win')
        if win_str == 'win':
            win = True
        elif win_str == 'loss':
            win = False
        else:
            win = None  # draw
        notes = request.POST.get('notes')
        team_id = request.POST.get('team')
        try:
            match.match_date = datetime.strptime(match_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            session.close()
            messages.error(request, 'Invalid date format.')
            return redirect('match_edit', match_id=match_id)
        match.rules = rules
        match.win = win
        match.notes = notes
        match.team_id = team_id
        session.commit()
        session.close()
        messages.success(request, 'Match updated successfully.')
        return redirect('match_list')
    session.close()
    # GET request: show form with teams and current match data
    session = get_session()
    teams = session.query(Team).all()
    session.close()
    return render(request, 'core/match_form.html', {'match': match, 'teams': teams})

def match_delete(request, match_id):
    session = get_session()
    match = session.query(Match).get(match_id)
    if match:
        session.delete(match)
        session.commit()
        session.close()
        messages.success(request, 'Match deleted successfully.')
    else:
        session.close()
        messages.error(request, 'Match not found.')
    return redirect('match_list')