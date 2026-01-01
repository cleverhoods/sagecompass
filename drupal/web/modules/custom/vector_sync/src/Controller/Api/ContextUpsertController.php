<?php

namespace Drupal\vector_sync\Controller\Api;

use Drupal\node\Entity\Node;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Drupal\Core\Controller\ControllerBase;
use Drupal\taxonomy\Entity\Term;

class ContextUpsertController extends ControllerBase {

  public function upsert(Request $request) {
    $data = json_decode($request->getContent(), TRUE);

    if (!$data || empty($data['title']) || empty($data['description'])) {
      return new JsonResponse(['success' => FALSE, 'message' => 'Invalid payload'], 400);
    }

    $title = $data['title'];
    $desc = $data['description'];
    $tags = $data['tags'] ?? [];
    $agents = $data['agents'] ?? [];

    $tag_entities = $this->getOrCreateTerms($tags, 'generic_tags');
    $agent_entities = $this->getOrCreateTerms($agents, 'agents');

    $hash = $this->generateHash($agent_entities, $tag_entities, $title, $desc);

    $nids = \Drupal::entityQuery('node')
      ->condition('type', 'context')
      ->condition('field_hash', $hash)
      ->accessCheck()
      ->execute();

    if (!empty($nids)) {
      $node = Node::load(reset($nids));
    }
    else {
      $node = Node::create(['type' => 'context']);
    }

    $node->setTitle($title);
    $node->set('field_description', $desc);
    $node->set('field_agents', array_map(fn($term) => $term->id(), $agent_entities));
    $node->set('field_tags', array_map(fn($term) => $term->id(), $tag_entities));
    $node->set('field_hash', $hash);
    $node->setNewRevision(TRUE);
    $node->save();

    return new JsonResponse(['success' => TRUE, 'uuid' => $node->uuid()]);
  }

  private function getOrCreateTerms(array $names, string $vocabulary) {
    $terms = [];
    foreach ($names as $name) {
      $query = \Drupal::entityTypeManager()->getStorage('taxonomy_term')->getQuery();
      $query->condition('vid', $vocabulary);
      $query->condition('name', $name);
      $tids = $query->execute();

      if (!empty($tids)) {
        $term = Term::load(reset($tids));
      }
      else {
        $term = Term::create([
          'vid' => $vocabulary,
          'name' => $name,
        ]);
        $term->save();
      }
      $terms[] = $term;
    }
    return $terms;
  }

  private function generateHash(array $agents, array $tags, string $title, string $desc) {
    $agent_keys = array_map(fn($term) => strtolower($term->label()), $agents);
    $tag_keys = array_map(fn($term) => strtolower($term->label()), $tags);

    sort($agent_keys);
    sort($tag_keys);

    $title = trim(strtolower(strip_tags($title)));
    $desc = trim(strtolower(strip_tags($desc)));

    $source_string = implode('|', [
      implode(',', $agent_keys),
      implode(',', $tag_keys),
      $title,
      $desc,
    ]);

    return hash('sha256', $source_string);
  }
}
