from django.shortcuts import render, redirect, get_object_or_404
from .forms import JournalForm
from .models import Journal
from django.contrib.auth.decorators import permission_required
import os
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages


def journal(request):
    """Vue d'accueil de la liste des journaux"""
    journals = Journal.objects.all().order_by('-number')
    paginator = Paginator(journals, 3)  # 3 journaux par page
    page = request.GET.get('page')

    try:
        journals = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, on affiche la première page
        journals = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites, on affiche la dernière page
        journals = paginator.page(paginator.num_pages)
    context = {'journals': journals}
    return render(request, 'journal/journal.html', context)


@permission_required('journal.view_journal')
def list_journals(request):
    """Vue de la liste des journaux pour l'administrateur"""
    journaux = Journal.objects.all().order_by('-number')
    return render(request, 'journal/list_journals.html',
                  {'journaux': journaux})


@permission_required('journal.add_journal')
def add_journal(request):
    """Vue d'ajout de journal pour l'administrateur"""
    if request.method == 'POST':
        journal_form = JournalForm(request.POST, request.FILES)
        if journal_form.is_valid():
            journal_form.save()
            messages.success(request, "Le journal a été ajouté avec succès.")
            return redirect('journal:admin_journaux_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        journal_form = JournalForm()

    return render(request, 'journal/add_journal.html',
                  {'journal': journal_form})


@permission_required('journal.delete_journal')
def delete_journal(request, id):
    """Vue de suppression de journal pour l'administrateur"""
    journal = get_object_or_404(Journal, id=id)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            # Récupérer les chemins des fichiers
            document = journal.document.path
            cover = journal.cover.path

            # Vérifier si les fichiers existent
            # Puis les supprimer
            if os.path.exists(document):
                os.remove(document)
            if os.path.exists(cover):
                os.remove(cover)
            journal.delete()
            messages.success(request, "Le journal a été supprimé avec succès.")
            return redirect('journal:admin_journaux_list')
        else:
            messages.error(request, "La suppression a été annulée.")
            return redirect('journal:admin_journaux_list')
    else:
        return render(request, 'journal/delete_journal.html',
                               {'journal': journal})


@permission_required('journal.change_journal')
def edit_journal(request, id):
    """Vue d'édition de journal pour l'administrateur"""
    journal = get_object_or_404(Journal, id=id)

    # On garde documents actuels en mémoire
    # pour les supprimer si ils sont remplacés
    last_document = journal.document
    last_cover = journal.cover

    if request.method == 'POST':
        journal_form = JournalForm(request.POST, request.FILES,
                                   instance=journal)

        if journal_form.is_valid():
            journal = journal_form.save(commit=False)
            # Vérifier si les fichiers ont changé
            import os
            indisponible = False
            indisponible_files = []
            # Vérification existence fichiers avant suppression
            if journal.document != last_document:
                if last_document and hasattr(last_document, 'path'):
                    if os.path.exists(last_document.path):
                        os.remove(last_document.path)
                    else:
                        indisponible = True
                        indisponible_files.append('document')
            if journal.cover != last_cover:
                if last_cover and hasattr(last_cover, 'path'):
                    if os.path.exists(last_cover.path):
                        os.remove(last_cover.path)
                    else:
                        indisponible = True
                        indisponible_files.append('couverture')
            journal.save()
            if indisponible:
                msg = "Fichier(s) suivant(s) non trouvé(s) sur le serveur : " + ", ".join(indisponible_files) + ". Ils ont été marqués comme 'Indisponible'."
                messages.warning(request, msg)
            else:
                messages.success(request, "Le journal a été modifié avec succès.")
            return redirect('journal:admin_journaux_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        journal_form = JournalForm(instance=journal)

    return render(request, 'journal/edit_journal.html',
                  {'journal': journal_form})
